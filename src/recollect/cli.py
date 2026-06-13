from __future__ import annotations

import argparse
import json
import sys

from recollect import __version__
from recollect.config import RecollectConfig
from recollect.memory import Memory


def cmd_demo(args: argparse.Namespace) -> int:
    config = RecollectConfig.local_dev()
    if args.data_dir:
        config = config.model_copy(update={"data_dir": args.data_dir})
    memory = Memory(config)
    uid = args.user_id

    samples = [
        "User prefers dark mode and vim keybindings",
        "User is allergic to shellfish",
        "User timezone is America/Los_Angeles",
    ]
    for text in samples:
        memory.add(text, user_id=uid, infer=False)

    query = args.query or "editor and food preferences"
    result = memory.search(query, filters={"user_id": uid}, top_k=3)
    print(f"Query: {query}")
    print(json.dumps(result, indent=2, default=str))
    memory.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recollect", description="Recollect memory CLI")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit",
    )
    sub = parser.add_subparsers(dest="command", required=False)

    demo = sub.add_parser("demo", help="Seed sample memories and run a search")
    demo.add_argument("--user-id", default="demo_user")
    demo.add_argument("--query", default=None)
    demo.add_argument("--data-dir", default=None)
    demo.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
