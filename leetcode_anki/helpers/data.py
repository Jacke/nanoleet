# pylint: disable=missing-module-docstring
import functools
import json
import logging
import math
import time
from functools import cached_property
from typing import Any, Callable, Dict, List
from abc import ABCMeta, abstractmethod
from tqdm import tqdm  # type: ignore
import urllib3  # type: ignore
from urllib3.exceptions import ProtocolError  # type: ignore
from leetcode.api.default_api import DefaultApi  # type: ignore
import leetcode.models.graphql_query  # type: ignore
import leetcode.models.graphql_query_get_question_detail_variables  # type: ignore
import leetcode.models.graphql_query_problemset_question_list_variables  # type: ignore
import leetcode.models.graphql_query_problemset_question_list_variables_filter_input  # type: ignore
import leetcode.models.graphql_question_detail  # type: ignore
from leetcode.models.graphql_question_detail import GraphqlQuestionDetail  # type: ignore
from leetcode_anki.helpers.api import retry, _get_leetcode_api_client
from csv_reader import OLLEntity

CACHE_DIR = "cache"

class GraphqlQuestionDetailWithOLL:
    def __init__(self, details: GraphqlQuestionDetail, oll_desc: OLLEntity) -> None:
        self.details: GraphqlQuestionDetail = details
        self.oll_desc: OLLEntity = oll_desc

class LeetcodeData(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '_get_problem_data') and
                callable(subclass._get_problem_data) or
                NotImplemented)

    @cached_property
    def api_instance(self) -> DefaultApi:
        return _get_leetcode_api_client()

    @abstractmethod
    async def _get_problem_data(self, problem_slug: str) -> GraphqlQuestionDetail:
        pass

    async def _get_description(self, problem_slug: str) -> str:
        """
        Problem description
        """
        data = self._get_problem_data(problem_slug)
        return data.content or "No content"  # type: ignore

    async def _stats(self, problem_slug: str) -> Dict[str, str]:
        """
        Various stats about problem. Such as number of accepted solutions, etc.
        """
        data = self._get_problem_data(problem_slug)
        logging.info("_stats %s", data)
        return json.loads(data.stats)  # type: ignore

    async def submissions_total(self, problem_slug: str) -> int:
        """
        Total number of submissions of the problem
        """
        return int((await self._stats(problem_slug))["totalSubmissionRaw"])

    async def submissions_accepted(self, problem_slug: str) -> int:
        """
        Number of accepted submissions of the problem
        """
        return int((await self._stats(problem_slug))["totalAcceptedRaw"])

    async def description(self, problem_slug: str) -> str:
        """
        Problem description
        """
        return await self._get_description(problem_slug)

    async def difficulty(self, problem_slug: str) -> str:
        """
        Problem difficulty. Returns colored HTML version, so it can be used
        directly in Anki
        """
        data = self._get_problem_data(problem_slug)
        diff = data.difficulty  # type: ignore

        if diff == "Easy":
            return "<font color='green'>Easy</font>"

        if diff == "Medium":
            return "<font color='orange'>Medium</font>"

        if diff == "Hard":
            return "<font color='red'>Hard</font>"

        raise ValueError(f"Incorrect difficulty: {diff}")

    async def paid(self, problem_slug: str) -> str:
        """
        Problem's "available for paid subsribers" status
        """
        data = self._get_problem_data(problem_slug)  # type: ignore
        return data.is_paid_only  # type: ignore

    async def problem_id(self, problem_slug: str) -> str:
        """
        Numerical id of the problem
        """
        data = self._get_problem_data(problem_slug)
        return data.question_frontend_id  # type: ignore

    async def likes(self, problem_slug: str) -> int:
        """
        Number of likes for the problem
        """
        data = self._get_problem_data(problem_slug)
        likes = data.likes  # type: ignore

        if not isinstance(likes, int):
            raise ValueError(f"Likes should be int: {likes}")

        return likes

    async def dislikes(self, problem_slug: str) -> int:
        """
        Number of dislikes for the problem
        """
        data = self._get_problem_data(problem_slug)
        dislikes = data.dislikes  # type: ignore

        if not isinstance(dislikes, int):
            raise ValueError(f"Dislikes should be int: {dislikes}")

        return dislikes

    async def tags(self, problem_slug: str) -> List[str]:
        """
        List of the tags for this problem (string slugs)
        """
        data = self._get_problem_data(problem_slug)
        tags = list(map(lambda x: x.slug, data.topic_tags))  # type: ignore
        # type: ignore
        tags.append(f"difficulty-{data.difficulty.lower()}-tag")
        return tags

    async def freq_bar(self, problem_slug: str) -> float:
        """
        Returns percentage for frequency bar
        """
        data = self._get_problem_data(problem_slug)
        return data.freq_bar or 0  # type: ignore

    async def hint(self, problem_slug: str) -> float:
        """
        Returns percentage for frequency bar
        """
        data = self._get_problem_data(problem_slug)
        return data.hints or ""  # type: ignore

    async def title(self, problem_slug: str) -> float:
        """
        Returns problem title
        """
        data = self._get_problem_data(problem_slug)
        return data.title  # type: ignore

    async def category(self, problem_slug: str) -> float:
        """
        Returns problem category title
        """
        data = self._get_problem_data(problem_slug)
        return data.category_title  # type: ignore

    async def all_problems_handles(self) -> List[str]:
        """
        Get all problem handles known.

        Example: ["two-sum", "three-sum"]
        """
        return list(self._cache.keys()) # type: ignore

class LeetcodeSlugData(LeetcodeData):
    def __init__(self, problem_to_parse: List[OLLEntity]) -> None:
        self.problem_to_parse = problem_to_parse

    def get_problems(self):
        problems = []
        for problem in self.problem_to_parse[:5]:
            logging.info("get problem: %s", problem.slug)
            problems.extend(self._get_problems_data(problem))
        logging.info("problems count: %s", len(problems))
        return problems

    @cached_property
    def _cache(
        self,
    ) -> Dict[str, GraphqlQuestionDetail]:
        """
        Cached method to return dict (problem_slug -> question details)
        """
        problems = self.get_problems()
        return {problem.details.title_slug: problem for problem in problems}

    @retry(times=3, exceptions=(ProtocolError,), delay=5)
    # type: ignore
    def _get_problems_data(self, problem) -> List[GraphqlQuestionDetail]:
        api_instance = self.api_instance
        graphql_request = leetcode.models.graphql_query.GraphqlQuery(
            query="""
                query questionContent($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        content
                        questionId
                        questionFrontendId
                        title
                        titleSlug
                        isPaidOnly
                        difficulty
                        likes
                        dislikes
                        categoryTitle
                        freqBar
                        topicTags {
                            name
                            slug
                        }
                        stats
                        hints
                    }
                }
            """,
            variables=leetcode.models.graphql_query_get_question_detail_variables.GraphqlQueryGetQuestionDetailVariables(
                title_slug=problem.slug,
            ),
            operation_name="questionContent",
        )
        time.sleep(2)  # Leetcode has a rate limiter
        problems = []
        try:
            data = api_instance.graphql_post(body=graphql_request).data
            question_detail = data.question
            problems.append(GraphqlQuestionDetailWithOLL(question_detail, problem))
        finally:
            return problems

    def _get_problem_data(
        self, problem_slug: str
    ) -> GraphqlQuestionDetail:
        cache = self._cache
        if problem_slug in cache:
            return cache[problem_slug].details # type: ignore
        raise ValueError(f"Problem {problem_slug} is not in cache")

    def _get_oll_data(
        self, problem_slug: str
    ) -> OLLEntity:
        cache = self._cache
        if problem_slug in cache:
            return cache[problem_slug].oll_desc # type: ignore

        raise ValueError(f"Problem {problem_slug} is not in cache")

    async def oll_short(self, problem_slug: str) -> str:
        data = self._get_oll_data(problem_slug)
        extracted = data.oll_short.replace("[","").replace("]","")
        return extracted.split(",") if extracted != "" else ""

    async def oll_desc(self, problem_slug: str) -> str:
        data = self._get_oll_data(problem_slug)
        return data.oll_desc or ""  # type: ignore

class LeetcodePageData(LeetcodeData):
    """
    Retrieves and caches the data for problems, acquired from the leetcode API by page.

    This data can be later accessed using provided methods with corresponding
    names.
    """

    def __init__(
        self, start: int, stop: int, page_size: int = 1000, list_id: str = ""
    ) -> None:
        """
        Initialize leetcode API and disk cache for API responses
        """
        if start < 0:
            raise ValueError(f"Start must be non-negative: {start}")

        if stop < 0:
            raise ValueError(f"Stop must be non-negative: {start}")

        if page_size < 0:
            raise ValueError(f"Page size must be greater than 0: {page_size}")

        if start > stop:
            raise ValueError(
                f"Start (){start}) must be not greater than stop ({stop})")

        self._start = start
        self._stop = stop
        self._page_size = page_size
        self._list_id = list_id

    @cached_property
    def _cache(
        self,
    ) -> Dict[str, GraphqlQuestionDetail]:
        """
        Cached method to return dict (problem_slug -> question details)
        """
        problems = self._get_problems_data()
        return {problem.title_slug: problem for problem in problems}

    @retry(times=3, exceptions=(ProtocolError,), delay=5)
    def _get_problems_count(self) -> int:
        api_instance = self.api_instance

        graphql_request = leetcode.models.graphql_query.GraphqlQuery(
            query="""
            query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
              problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
              ) {
                totalNum
              }
            }
            """,
            variables=leetcode.models.graphql_query_problemset_question_list_variables.GraphqlQueryProblemsetQuestionListVariables(
                category_slug="",
                limit=1,
                skip=0,
                filters=leetcode.models.graphql_query_problemset_question_list_variables_filter_input.GraphqlQueryProblemsetQuestionListVariablesFilterInput(
                    tags=[],
                    list_id=self._list_id
                    # difficulty="MEDIUM",
                    # status="NOT_STARTED",
                    # list_id="7p5x763",  # Top Amazon Questions
                    # premium_only=False,
                ),
            ),
            operation_name="problemsetQuestionList",
        )

        time.sleep(2)  # Leetcode has a rate limiter
        data = api_instance.graphql_post(body=graphql_request).data
        return data.problemset_question_list.total_num or 0

    @retry(times=3, exceptions=(ProtocolError,), delay=5)
    def _get_problems_data_page(
        self, offset: int, page_size: int, page: int
    ) -> List[GraphqlQuestionDetail]:
        api_instance = self.api_instance
        graphql_request = leetcode.models.graphql_query.GraphqlQuery(
            query="""
            query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
              problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
              ) {
                questions: data {
                    questionFrontendId
                    title
                    titleSlug
                    categoryTitle
                    freqBar
                    content
                    isPaidOnly
                    difficulty
                    likes
                    dislikes
                    topicTags {
                      name
                      slug
                    }
                    stats
                    hints
                }
              }
            }
            """,
            variables=leetcode.models.graphql_query_problemset_question_list_variables.GraphqlQueryProblemsetQuestionListVariables(
                category_slug="",
                limit=page_size,
                skip=offset + page * page_size,
                filters=leetcode.models.graphql_query_problemset_question_list_variables_filter_input.GraphqlQueryProblemsetQuestionListVariablesFilterInput(
                    list_id=self._list_id
                ),
            ),
            operation_name="problemsetQuestionList",
        )

        time.sleep(2)  # Leetcode has a rate limiter
        data = api_instance.graphql_post(
            body=graphql_request
        ).data.problemset_question_list.questions

        return data

    def _get_problems_data(
        self,
    ) -> List[GraphqlQuestionDetail]:
        problem_count = self._get_problems_count()

        if self._start > problem_count:
            raise ValueError(
                "Start ({self._start}) is greater than problems count ({problem_count})"
            )

        start = self._start
        stop = min(self._stop, problem_count)

        page_size = min(self._page_size, stop - start + 1)

        problems: List[
            GraphqlQuestionDetail
        ] = []

        logging.info("Fetching %s problems %s per page",
                     stop - start + 1, page_size)

        for page in tqdm(
            range(math.ceil((stop - start + 1) / page_size)),
            unit="problem",
            unit_scale=page_size,
        ):
            data = self._get_problems_data_page(start, page_size, page)
            problems.extend(data)

        return problems

    def _get_problem_data(
        self, problem_slug: str
    ) -> GraphqlQuestionDetail:
        cache = self._cache
        if problem_slug in cache:
            return cache[problem_slug]
        raise ValueError(f"Problem {problem_slug} is not in cache")
