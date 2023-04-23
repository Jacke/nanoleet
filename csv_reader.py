#!/usr/bin/env python3
"""
This script generates an Anki deck with all the leetcode problems currently
known.
"""

import csv
from typing import List


class OLLEntity:
    def __init__(self, slug, oll_short, oll_desc) -> None:
        self.slug = slug
        self.oll_short = oll_short
        self.oll_desc = oll_desc


class OLLEntry:
    def __init__(self, title, url, level, category, oll_short, oll_desc) -> None:
        self.title = title
        self.url = url
        self.level = level
        self.category = category
        self.oll_short = oll_short
        self.oll_desc = oll_desc

    def __repr__(self):
        return f"OLLEntry({self.title!r}, {self.url!r}, {self.level!r}, {self.category!r}, {self.oll_short!r}, {self.oll_desc!r})"

    def get_slug(self) -> OLLEntity:
        return OLLEntity(self.url.replace("https://leetcode.com/problems/", "").replace("/", ""), self.oll_short, self.oll_desc)


def parse_oll_csv(path: str) -> List[OLLEntry]:
    with open(path, newline='') as csvfile:
        leets = csv.reader(csvfile, delimiter=',', quotechar='"')
        acc = []
        next(leets)
        for row in leets:
            oll_entry = OLLEntry(*row)
            acc.append(oll_entry)
        return acc
