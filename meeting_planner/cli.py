"""Command line entry points: help, version and the serve and solve commands."""

import argparse
import sys

from . import __version__

# Command -> parent ticket that builds it.
_PLANNED = {"serve": 2, "solve": 4}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="meeting_planner", description="Offline time zone meeting planner.")
    parser.add_argument("--version", action="version", version=f"meeting_planner {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="command")
    serve = sub.add_parser("serve", help="run the local app (not implemented yet)")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--data-dir", default="./data")
    solve = sub.add_parser("solve", help="solve a scenario file (not implemented yet)")
    solve.add_argument("scenario")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    print(f"not implemented yet: see #{_PLANNED[args.command]}", file=sys.stderr)
    return 1
