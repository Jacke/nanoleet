#!/usr/bin/env python3
import argparse
import asyncio
import logging

from anki.generate import generate, PageBasedArg, CollectionBasedArg
logging.getLogger().setLevel(logging.INFO)

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the script
    """
    parser = argparse.ArgumentParser(description="Generate Anki cards and PDF for leetcode tasks")
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_a = subparsers.add_parser('a', help='a help')
    parser_a.add_argument('bar', type=int, help='bar help')
    parser_b = subparsers.add_parser('b', help='b help')
    parser_b.add_argument('--baz', choices='XYZ', help='baz help')

    # by_page = parser.add_argument_group('All problems')
    # oll_collections = parser.add_argument_group('One Line Leet problems')
    # by_page.add_argument(
        # "--start", type=int, help="Start generation from this problem", default=0
    # )
    # by_page.add_argument(
        # "--stop", type=int, help="Stop generation on this problem", default=2**12
    # )
    # by_page.add_argument(
        # "--page-size",
        # type=int,
        # help="Get at most this many problems (decrease if leetcode API times out)",
        # default=100,
    # )
    # by_page.add_argument(
        # "--list-id",
        # type=str,
        # help="Get all questions by list (leetcode.com/list?selectedList=<list_id>",
        # default="",
    # )
    # oll_collections.add_argument(
        # "--csv", type=str, help="One line leet custom CSV", default=""
    # )
    # parser.add_argument(
        # "--output-file", type=str, help="Output filename", default=OUTPUT_FILE
    # )
    args = parser.parse_args()
    return args

async def main() -> None:
    """
    The main script logic
    """
    args = parse_args()
    # start, stop, page_size, list_id, output_file = (
        # args.start,
        # args.stop,
        # args.page_size,
        # args.list_id,
        # args.output_file,
    # )
    PageBasedArg(
        1,
        2,
        3,
        "11",
        "generated/"
    )
    app_arg = CollectionBasedArg()
    await generate(app_arg)

if __name__ == "__main__":
    loop: asyncio.events.AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main()) # asyncio.run(main(loop=loop))
    except KeyboardInterrupt:
        pass

# employee.py

from datetime import date

class Employee:
    def __init__(self, name, birth_date):
        self.name = name
        self.birth_date = birth_date

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.upper()

    @property
    def birth_date(self):
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value):
        self._birth_date = date.fromisoformat(value)


