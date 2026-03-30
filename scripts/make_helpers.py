"""Helper commands used by the project Makefile."""

from __future__ import annotations

import argparse
import importlib.util
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from collections.abc import Sequence


def _clean_sys_path() -> None:
    cwd = os.getcwd()
    sys.path = [path for path in sys.path if os.path.abspath(path or os.curdir) != cwd]


def _run(command: Sequence[str]) -> str:
    return subprocess.check_output(command, text=True).strip()


def _project_version() -> str:
    return _run([sys.executable, "-m", "commitizen", "version", "--project"])


def _release_tag() -> str:
    return f"v{_project_version()}"


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

    subprocess.check_call(["git", "fetch", "--quiet", remote, branch, "--tags"])
    behind = _run(["git", "rev-list", "--count", f"HEAD..{remote}/{branch}"])

    if behind != "0":
        print(
            f"Local branch '{branch}' is behind '{remote}/{branch}'. "
            "Sync the branch first."
        )
        return 1

    return 0


def build(_: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "-c",
        (
            "import os, runpy, sys; "
            "cwd = os.getcwd(); "
            "sys.path = [p for p in sys.path if os.path.abspath(p or os.curdir) != cwd]; "
            "sys.argv = ['pyproject-build']; "
            "runpy.run_module('build', run_name='__main__')"
        ),
    ]
    result = subprocess.run(command, text=True, capture_output=True)

    if result.returncode != 0:
        if result.stdout.strip():
            print(result.stdout.strip(), file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return result.returncode

    return 0


def check_release_commits(_: argparse.Namespace) -> int:
    try:
        subprocess.check_output(
            [sys.executable, "-m", "commitizen", "bump", "--get-next"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as error:
        output = (error.output or "").strip()
        if "[NO_COMMITS_TO_BUMP]" in output:
            print("No release-eligible commits found since the latest tag.")
            return 1

        if output:
            print(output)
        return error.returncode

    return 0


def push_release_tag(args: argparse.Namespace) -> int:
    tag = _release_tag()
    subprocess.check_call(["git", "push", "--quiet", args.remote, tag])
    return 0


def write_release_notes(args: argparse.Namespace) -> int:
    changelog_path = Path(args.changelog)
    output_path = Path(args.output)
    version = args.version

    changelog = changelog_path.read_text(encoding="utf-8")
    lines = changelog.splitlines()

    header = f"## {version}"
    start = None

    for index, line in enumerate(lines):
        if line.startswith(header):
            start = index
            break

    if start is None:
        print(f"Release notes section '{version}' not found in {changelog_path}.")
        return 1

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    section = "\n".join(lines[start:end]).strip() + "\n"
    output_path.write_text(section, encoding="utf-8")
    print(f"Release notes written to {output_path}.")
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

    parser_check_release_commits = subparsers.add_parser("check-release-commits")
    parser_check_release_commits.set_defaults(handler=check_release_commits)

    parser_push_release_tag = subparsers.add_parser("push-release-tag")
    parser_push_release_tag.add_argument("--remote", required=True)
    parser_push_release_tag.set_defaults(handler=push_release_tag)

    parser_write_release_notes = subparsers.add_parser("write-release-notes")
    parser_write_release_notes.add_argument("--version", required=True)
    parser_write_release_notes.add_argument("--changelog", required=True)
    parser_write_release_notes.add_argument("--output", required=True)
    parser_write_release_notes.set_defaults(handler=write_release_notes)

    return parser


def main() -> int:
    parser = _create_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
