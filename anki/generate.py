#!/usr/bin/env python3
"""
This script generates an Anki deck with all the leetcode problems currently
known.
"""
import logging

# https://github.com/kerrickstaley/genanki
import genanki
from tqdm import tqdm  # type: ignore
from leetcode_anki.models import generate_anki_note, LeetcodeNote, LeetcodeAnkiFactory
from leetcode_anki.helpers.data import LeetcodeData, LeetcodePageData, LeetcodeSlugData
from leetcode_anki.helpers.api import _get_leetcode_api_client
from leetcode import GraphqlQuery, GraphqlQueryVariables
from csv_reader import parse_oll_csv
from typing import Awaitable, List
from pathlib import Path

LEETCODE_ANKI_DECK_ID = 8589798175
OUTPUT_FILE = "leetcode.apkg"
OUTPUT_DIR = "generated/"


class AppArguments:
    def __init__(self, output_dir):
        self.output_dir = output_dir


class PageBasedArg(AppArguments):
    def __init__(self, start, stop, page_size, list_id, output_dir=OUTPUT_DIR) -> None:
        self.start = start
        self.stop = stop
        self.page_size = page_size
        self.list_id = list_id
        self.output_dir = output_dir


class CollectionBasedArg(AppArguments):
    def __init__(self, output_dir=OUTPUT_DIR, csv_path="data/one_line_leet.data.csv") -> None:
        self.output_dir = output_dir
        self.csv_path = csv_path


async def gen_leetcode_cards():
    print("ok")


async def generate(args: AppArguments) -> None:
    """
    Generate an Anki deck
    """
    print("CollectionBasedArg %s", isinstance(args, CollectionBasedArg))
    print("PageBasedArg %s", isinstance(args, PageBasedArg))
    leetcode_model = LeetcodeAnkiFactory.nano_leet()

##########################################################################################################################################
    graphql_request = GraphqlQuery(
        query="""
    {
    user {
        username
        isCurrentUserPremium
    }
    }
        """,
        variables=GraphqlQueryVariables(),
    )
    logging.info(_get_leetcode_api_client().graphql_post(
        body=graphql_request).__dict__)
    nano_leet_entries = parse_oll_csv('data/one_line_leet.data.csv')
    slugs_with_desc = list(map(lambda x: x.get_slug(), nano_leet_entries))
    leetcode_data = LeetcodeSlugData(slugs_with_desc)
    logging.info(
        f"OLL Entries parsed count: {len(slugs_with_desc)} {slugs_with_desc[0]}")
# logging.info("leetcode model:", leetcode_model.__dict__)
# Temp disabled
    leetcode_deck = genanki.Deck(LEETCODE_ANKI_DECK_ID, Path(
        args.output_dir + OUTPUT_FILE).stem)
    # leetcode_data = LeetcodePageData(
    # start, stop, page_size, list_id
    # )
    note_generators: List[LeetcodeNote] = []
    task_handles = await leetcode_data.all_problems_handles()
    logging.info("Generating flashcards")
    for leetcode_task_handle in task_handles:
        note_generators.append(
            await generate_anki_note(leetcode_data, leetcode_model, leetcode_task_handle)
        )
    for leetcode_note in tqdm(note_generators, unit="flashcard"):
        if (leetcode_note).model:
            logging.info("note: %s", (leetcode_note).model.to_json(0, 0))
        leetcode_deck.add_note(leetcode_note)
    genanki.Package(leetcode_deck).write_to_file(args.output_dir + OUTPUT_FILE)
