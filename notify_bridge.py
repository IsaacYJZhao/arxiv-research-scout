"""
notify_bridge.py — 把 arxiv-research-scout 的检索结果送到桌宠的通知收件箱。

放在项目根目录（和 pyproject.toml 同级）。

--------------------------------------------------------------------
两种模式
--------------------------------------------------------------------

默认（云端为主，推荐）：

    python notify_bridge.py

    检索由 GitHub Actions 完成，本脚本只负责"把云端结果同步到本地
    并通知你"：

      1. git fetch，看远端有没有新的 bot 提交；
      2. 没有新提交就安静退出，不发通知；
      3. 有新提交就 fast-forward 合并下来——这一步同时把
         reports/ 里的论文报告和 digest 落到本地磁盘；
      4. 对比合并前后 .state/state.json 里的 processed_ids，
         差集就是这一轮新分析的论文，据此拼一条桌宠通知。

    这样电脑关机期间云端照常检索，开机后第一次运行就能补上通知，
    而且本地不再单独维护一份状态、不会和云端打架。

    默认只在"确实有新论文"时才打扰你。云端跑完但一篇都没入选时
    不发通知；想用通知确认系统还活着，加 --notify-empty。

应急/离线（本地跑一次完整分析）：

    python notify_bridge.py --local
    python notify_bridge.py --local --force

    行为和旧版一致：直接调用 arxiv-scout run。需要本地配好
    DEEPSEEK_API_KEY。注意这会写本地 .state/state.json，
    在"云端为主"的模式下属于临时手段，跑完记得把改动提交推送，
    否则下次云端 rebase 会冲突。

--------------------------------------------------------------------
设计约束
--------------------------------------------------------------------

本脚本只读项目对外的公开产物（.state/state.json 和 reports/ 目录），
不 import 项目内部模块，所以升级项目版本一般不会破坏它。只有当项目
改了 state.json 的字段名或 reports/ 的命名规则时，才需要跟着改下面
的常量和 find_report_path()。
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
STATE_FILE = PROJECT_DIR / ".state" / "state.json"
REPORTS_DIR = PROJECT_DIR / "reports"
DIGESTS_DIR = REPORTS_DIR / "digests"

# 手动对比用的报告，不属于自动检索产物，不参与通知
EXCLUDED_REPORT_DIRS = {"manual"}

APP_NAME = "DesktopPetMemo"

GIT_TIMEOUT_SECONDS = 120


# ====================================================================
# 桌宠收件箱
# ====================================================================


def pet_events_inbox() -> Path:
    """必须和 desktop_pet.py 的 _data_dir() Windows 分支保持一致。"""
    base = (
        os.environ.get("LOCALAPPDATA")
        or os.environ.get("APPDATA")
        or str(Path.home())
    )
    return Path(base) / APP_NAME / "events" / "inbox"


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, path)


def send_pet_event(payload: dict) -> Path:
    payload.setdefault("source", "arxiv")
    payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())

    event_path = (
        pet_events_inbox()
        / f"arxiv_{datetime.now():%Y%m%d%H%M%S}_{uuid.uuid4().hex[:8]}.json"
    )
    atomic_write_json(event_path, payload)
    print(f"Pet event written: {event_path}")
    return event_path


# ====================================================================
# 本地产物快照
# ====================================================================


def load_processed_ids() -> set[str]:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return set(data.get("processed_ids") or [])
    except (OSError, ValueError):
        return set()


def list_digests() -> set[str]:
    if not DIGESTS_DIR.is_dir():
        return set()
    return {path.name for path in DIGESTS_DIR.glob("*.md")}


def find_report_path(arxiv_id: str) -> Path | None:
    """
    在 reports/ 下按 arXiv ID 找报告。

    processed_ids 里存的是去掉版本号的 ID（2608.16855），而报告文件名
    带版本号（2608.16855v1.md），所以用前缀匹配。递归查找是为了兼容
    以后按 provider 或年份分子目录的情况；reports/manual/ 是本地手动
    对比产物，不算自动检索结果，排除掉。
    """
    if not REPORTS_DIR.is_dir():
        return None

    safe = arxiv_id.replace("/", "_")

    candidates = [
        path
        for path in REPORTS_DIR.rglob(f"{safe}*.md")
        if not (
            set(path.relative_to(REPORTS_DIR).parts[:-1])
            & EXCLUDED_REPORT_DIRS
        )
    ]

    return sorted(candidates)[0] if candidates else None


def latest_digest_path() -> Path | None:
    if not DIGESTS_DIR.is_dir():
        return None
    digests = sorted(DIGESTS_DIR.glob("*.md"))
    return digests[-1] if digests else None


# ====================================================================
# Git
# ====================================================================


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=GIT_TIMEOUT_SECONDS,
    )


def current_branch() -> str:
    result = git("rev-parse", "--abbrev-ref", "HEAD")
    branch = result.stdout.strip()
    return branch if result.returncode == 0 and branch else "main"


def working_tree_is_clean() -> bool:
    result = git("status", "--porcelain")
    return result.returncode == 0 and not result.stdout.strip()


def commits_behind(branch: str) -> int | None:
    result = git("rev-list", "--count", f"HEAD..origin/{branch}")
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


# ====================================================================
# 模式一：云端为主
# ====================================================================


def run_sync_mode(*, notify_empty: bool = False) -> int:
    before_ids = load_processed_ids()
    before_digests = list_digests()

    branch = current_branch()

    fetch = git("fetch", "origin", branch)
    if fetch.returncode != 0:
        # 断网、代理问题、仓库不可达等。安静失败，不发假通知。
        print("git fetch 失败，跳过本次同步：")
        print((fetch.stderr or fetch.stdout).rstrip())
        return 0

    behind = commits_behind(branch)
    if behind is None:
        print(f"无法比较本地与 origin/{branch}，跳过本次同步。")
        return 0

    if behind == 0:
        print(f"origin/{branch} 没有新提交，无需同步。")
        return 0

    print(f"origin/{branch} 有 {behind} 个新提交，准备同步。")

    if not working_tree_is_clean():
        # 有未提交的本地改动时 fast-forward 会失败。与其让脚本报错
        # 退出，不如明确告诉你一声，否则你会以为"最近没论文"。
        print("本地有未提交的改动，无法 fast-forward 合并。")
        print("请先提交或 stash 本地改动，再重新运行本脚本。")
        send_pet_event(
            {
                "title": "arXiv 结果同步被阻塞",
                "lines": [
                    f"origin/{branch} 有 {behind} 个新提交未同步",
                    "本地有未提交的改动，请先 commit 或 stash",
                ],
                "open_path": str(PROJECT_DIR),
            }
        )
        return 1

    merge = git("merge", "--ff-only", f"origin/{branch}")
    if merge.returncode != 0:
        print("fast-forward 合并失败：")
        print((merge.stderr or merge.stdout).rstrip())
        send_pet_event(
            {
                "title": "arXiv 结果同步失败",
                "lines": [
                    f"无法 fast-forward 到 origin/{branch}",
                    "本地与远端可能已分叉，需要手动处理",
                ],
                "open_path": str(PROJECT_DIR),
            }
        )
        return 1

    print(merge.stdout.rstrip())

    return notify_new_results(
        before_ids,
        before_digests,
        notify_empty=notify_empty,
    )


# ====================================================================
# 模式二：本地跑一次
# ====================================================================


def resolve_scout_command() -> list[str]:
    """优先用项目自带虚拟环境里安装的 arxiv-scout 命令行入口，
    找不到再退回用当前 Python 以 -m 方式跑（要求包已 pip install -e .）。"""
    venv_exe = PROJECT_DIR / ".venv" / "Scripts" / "arxiv-scout.exe"
    if venv_exe.exists():
        return [str(venv_exe), "run"]

    venv_python = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return [str(venv_python), "-m", "arxiv_research_scout.cli", "run"]

    return [sys.executable, "-m", "arxiv_research_scout.cli", "run"]


def run_local_mode(
    passthrough: list[str],
    *,
    notify_empty: bool = False,
) -> int:
    before_ids = load_processed_ids()
    before_digests = list_digests()

    cmd = resolve_scout_command() + passthrough
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout.rstrip())

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        print(f"arxiv-scout run 退出码非 0：{result.returncode}")
        # 退出码 1 表示部分论文失败，成功的那些仍然值得通知
        if result.returncode != 1:
            return result.returncode

    return notify_new_results(
        before_ids,
        before_digests,
        notify_empty=notify_empty,
    )


# ====================================================================
# 通知
# ====================================================================


def notify_new_results(
    before_ids: set[str],
    before_digests: set[str],
    *,
    notify_empty: bool = False,
) -> int:
    after_ids = load_processed_ids()
    after_digests = list_digests()

    new_ids = sorted(after_ids - before_ids)
    new_digests = sorted(after_digests - before_digests)

    print(f"新处理的论文数量：{len(new_ids)}")
    print(f"新增的 digest 数量：{len(new_digests)}")

    if not new_ids and not new_digests:
        print("没有新论文，跳过桌宠通知。")
        return 0

    if not new_ids and not notify_empty:
        # 云端跑完了但一篇都没入选。默认不打扰你；想确认系统还活着
        # 就加 --notify-empty。
        print("本轮没有入选论文，跳过桌宠通知（--notify-empty 可开启）。")
        return 0

    lines: list[str] = []
    open_path: str | None = None

    for arxiv_id in new_ids[:6]:
        report = find_report_path(arxiv_id)
        if report is not None and open_path is None:
            open_path = str(report)
        lines.append(f"{arxiv_id}（已生成报告）" if report else arxiv_id)

    if len(new_ids) > 6:
        lines.append(f"…等共 {len(new_ids)} 篇")

    if new_ids:
        title = f"检索到 {len(new_ids)} 篇新论文"
    else:
        # 云端跑完但一篇都没入选：digest 本身就是结论，值得看一眼
        title = "本轮检索没有新论文"
        lines.append("云端已完成一次检索，未选出新论文")

    if new_digests:
        lines.append(f"digest：{new_digests[-1]}")

    if open_path is None:
        digest = latest_digest_path()
        open_path = str(digest) if digest else None

    send_pet_event(
        {
            "title": title,
            "lines": lines,
            "open_path": open_path,
        }
    )
    return 0


# ====================================================================
# 入口
# ====================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="notify_bridge.py",
        description=(
            "把 arxiv-research-scout 的检索结果推送到桌宠通知收件箱。"
        ),
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help=(
            "在本地跑一次 arxiv-scout run，而不是同步 GitHub 上的结果。"
            "需要本地配置 API key。"
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "仅配合 --local 使用：跳过 run_every_days 的调度间隔检查。"
        ),
    )

    parser.add_argument(
        "--notify-empty",
        action="store_true",
        help=(
            "本轮没有入选论文时也发一条通知，用来确认系统仍在正常运行。"
        ),
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.local:
        passthrough = ["--force"] if args.force else []
        return run_local_mode(
            passthrough,
            notify_empty=args.notify_empty,
        )

    if args.force:
        print("--force 只在 --local 模式下有意义，已忽略。")

    return run_sync_mode(notify_empty=args.notify_empty)


if __name__ == "__main__":
    sys.exit(main())
