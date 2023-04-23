import genanki  # type: ignore
from leetcode_anki.helpers.data import LeetcodeData, LeetcodePageData, LeetcodeSlugData

LEETCODE_ANKI_MODEL_ID = 4567610856

class LeetcodeNote(genanki.Note):
    """
    Extended base class for the Anki note, that correctly sets the unique
    identifier of the note.
    """

    @property
    def guid(self) -> str:
        # Hash by leetcode task handle
        return genanki.guid_for(self.fields[0]) # type: ignore

class LeetcodeAnkiFactory:
    @staticmethod
    def plain():
        return genanki.Model(
            LEETCODE_ANKI_MODEL_ID,
            "Leetcode model",
            fields=[
                {"name": "Slug"},
                {"name": "Id"},
                {"name": "Title"},
                {"name": "Topic"},
                {"name": "Content"},
                {"name": "Difficulty"},
                {"name": "Paid"},
                {"name": "Likes"},
                {"name": "Dislikes"},
                {"name": "SubmissionsTotal"},
                {"name": "SubmissionsAccepted"},
                {"name": "SubmissionAcceptRate"},
                {"name": "Frequency"},
                {"name": "Hints"},
            ],
            templates=[
                {
                    "name": "Leetcode",
                    "qfmt": """
                    <h2>{{Id}}. {{Title}}</h2>
                    <b>Difficulty:</b> {{Difficulty}}<br/>
                    &#128077; {{Likes}} &#128078; {{Dislikes}}<br/>
                    <b>Submissions (total/accepted):</b>
                    {{SubmissionsTotal}}/{{SubmissionsAccepted}}
                    ({{SubmissionAcceptRate}}%)
                    <br/>
                    <b>Topic:</b> {{Topic}}<br/>
                    <b>Frequency:</b>
                    <progress value="{{Frequency}}" max="100">
                    {{Frequency}}%
                    </progress>
                    <br/>
                    <b>URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/'>
                        https://leetcode.com/problems/{{Slug}}/
                    </a>
                    <br/>
                    <h3>Description</h3>
                    {{Content}}
                    """,
                    "afmt": """
                    {{FrontSide}}
                    <hr id="answer">
                    <b>Discuss URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/discuss/'>
                        https://leetcode.com/problems/{{Slug}}/discuss/
                    </a>
                    <br/>
                    <b>Solution URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/solution/'>
                        https://leetcode.com/problems/{{Slug}}/solution/
                    </a>
                    <br/>
                    <b>Hints:</b>
                    {{Hints}}
                    """,
                }
            ],
        )
    @staticmethod
    def nano_leet():
        return genanki.Model(
            LEETCODE_ANKI_MODEL_ID,
            "Leetcode model",
            fields=[
                {"name": "Slug"},
                {"name": "Id"},
                {"name": "Title"},
                {"name": "Topic"},
                {"name": "Content"},
                {"name": "Difficulty"},
                {"name": "Paid"},
                {"name": "Likes"},
                {"name": "Dislikes"},
                {"name": "SubmissionsTotal"},
                {"name": "SubmissionsAccepted"},
                {"name": "SubmissionAcceptRate"},
                {"name": "Frequency"},
                {"name": "Hints"},
                {"name": "OLL Ways"},
                {"name": "OLL Description "},
            ],
            templates=[
                {
                    "name": "Leetcode",
                    "qfmt": """
                    <h2>{{Id}}. {{Title}}</h2>
                    <b>Difficulty:</b> {{Difficulty}}<br/>
                    &#128077; {{Likes}} &#128078; {{Dislikes}}<br/>
                    <b>Submissions (total/accepted):</b>
                    {{SubmissionsTotal}}/{{SubmissionsAccepted}}
                    ({{SubmissionAcceptRate}}%)
                    <br/>
                    <b>Topic:</b> {{Topic}}<br/>
                    <b>Frequency:</b>
                    <progress value="{{Frequency}}" max="100">
                    {{Frequency}}%
                    </progress>
                    <br/>
                    <b>URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/'>
                        https://leetcode.com/problems/{{Slug}}/
                    </a>
                    <br/>
                    <h3>Description</h3>
                    {{Content}}
                    """,
                    "afmt": """
                    {{FrontSide}}
                    <hr id="answer">
                    <b>Discuss URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/discuss/'>
                        https://leetcode.com/problems/{{Slug}}/discuss/
                    </a>
                    <br/>
                    <b>Solution URL:</b>
                    <a href='https://leetcode.com/problems/{{Slug}}/solution/'>
                        https://leetcode.com/problems/{{Slug}}/solution/
                    </a>
                    <br/>
                    <b>Hints:</b>
                    {{Hints}}
                    <br/>
                    <b>One Line Leet:</b>
                    <pre>{{oll_short}}</pre>
                    <p>{{oll_desc}}</p>
                    <br/>
                    """,
                }
            ],
        )

async def generate_anki_note(
    leetcode_data: LeetcodeData,
    leetcode_model: genanki.Model,
    leetcode_task_handle: str,
) -> LeetcodeNote:
    """
    Generate a single Anki flashcard
    """
    extra_fields = []
    if (isinstance(leetcode_data, LeetcodeSlugData)):
        extra_fields = [str(await leetcode_data.oll_short(leetcode_task_handle)), # type: ignore
                        str(await leetcode_data.oll_desc(leetcode_task_handle)), # type: ignore
        ]
    return LeetcodeNote(
        model=leetcode_model,
        fields=[
            leetcode_task_handle,
            str(await leetcode_data.problem_id(leetcode_task_handle)),
            str(await leetcode_data.title(leetcode_task_handle)),
            str(await leetcode_data.category(leetcode_task_handle)),
            await leetcode_data.description(leetcode_task_handle),
            await leetcode_data.difficulty(leetcode_task_handle),
            "yes" if await leetcode_data.paid(leetcode_task_handle) else "no",
            str(await leetcode_data.likes(leetcode_task_handle)),
            str(await leetcode_data.dislikes(leetcode_task_handle)),
            str(await leetcode_data.submissions_total(leetcode_task_handle)),
            str(await leetcode_data.submissions_accepted(leetcode_task_handle)),
            str(
                int(
                    await leetcode_data.submissions_accepted(leetcode_task_handle)
                    / await leetcode_data.submissions_total(leetcode_task_handle)
                    * 100
                )
            ),
            str(await leetcode_data.freq_bar(leetcode_task_handle)),
            str(await leetcode_data.hint(leetcode_task_handle)),
        ],#.extend(extra_fields),
        tags=await leetcode_data.tags(leetcode_task_handle),
        # FIXME: sort field doesn't work doesn't work
        sort_field=str(await leetcode_data.freq_bar(leetcode_task_handle)).zfill(3),
    )
