"""Helper commands used by the project Makefile."""

from __future__ import annotations

import argparse
import importlib.util
import os
import runpy
import shutil
import subprocess
import sys
from collections.abc import Sequence


def _clean_sys_path() -> None:
    cwd = os.getcwd()
    sys.path = [path for path in sys.path if os.path.abspath(path or os.curdir) != cwd]


def _run(command: Sequence[str]) -> str:
    return subprocess.check_output(command, text=True).strip()


def check_tools(_: argparse.Namespace) -> int:
    _clean_sys_path()

    missing: list[str] = []
    if shutil.which("git") is None:
        missing.append("git")

    modules = ("pip", "pytest", "ruff", "commitizen", "build")
    for module in modules:
        if importlib.util.find_spec(module) is None:
            missing.append(module)

    if missing:
        print(f"Missing tools: {', '.join(missing)}")
        return 1

    print("All tools are available.")
    return 0


def check_branch(args: argparse.Namespace) -> int:
    branch = _run(["git", "branch", "--show-current"])
    allowed = set(args.allowed_branches.split())

    if branch not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        print(
            f"Current branch is '{branch}'. Release must be created from one of: "
            f"{allowed_text}."
        )
        return 1

    return 0


def check_clean(_: argparse.Namespace) -> int:
    dirty = bool(_run(["git", "status", "--porcelain"]))

    if dirty:
        print("Working tree has uncommitted changes.")
        return 1

    return 0


def check_upstream(args: argparse.Namespace) -> int:
    branch = _run(["git", "branch", "--show-current"])
    remote = args.remote

    subprocess.check_call(["git", "fetch", remote, branch, "--tags"])
    behind = _run(["git", "rev-list", "--count", f"HEAD..{remote}/{branch}"])

    if behind != "0":
        print(
            f"Local branch '{branch}' is behind '{remote}/{branch}'. "
            "Sync the branch first."
        )
        return 1

    return 0


def build(_: argparse.Namespace) -> int:
    _clean_sys_path()
    sys.argv = ["pyproject-build"]
    runpy.run_module("build", run_name="__main__")
    return 0


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Makefile helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check_tools = subparsers.add_parser("check-tools")
    parser_check_tools.set_defaults(handler=check_tools)

    parser_check_branch = subparsers.add_parser("check-branch")
    parser_check_branch.add_argument("--allowed-branches", required=True)
    parser_check_branch.set_defaults(handler=check_branch)

    parser_check_clean = subparsers.add_parser("check-clean")
    parser_check_clean.set_defaults(handler=check_clean)

    parser_check_upstream = subparsers.add_parser("check-upstream")
    parser_check_upstream.add_argument("--remote", required=True)
    parser_check_upstream.set_defaults(handler=check_upstream)

    parser_build = subparsers.add_parser("build")
    parser_build.set_defaults(handler=build)

    return parser


def main() -> int:
    parser = _create_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
