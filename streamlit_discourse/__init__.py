import streamlit as st
from streamlit.proto.Exception_pb2 import Exception as ExceptionProto
from streamlit.elements.exception import _get_stack_trace_str_list

from contextlib import contextmanager

import re
import textwrap
import traceback
from typing import List, Iterable, Optional

from urllib.parse import urljoin, urlencode
import datetime
import pytz

import pandas as pd
import requests

BASE_URL = "https://discuss.streamlit.io"
TTL = 1 * 60 * 60  # 1 hour

_SPACES_RE = re.compile("\\s*")
_EMPTY_LINE_RE = re.compile("\\s*\n")

_ALLOWED_SORTS = ["latest", "likes", "views", "latest_topic"]
_ALLOWED_STATUSES = [
    "open",
    "closed",
    "public",
    "archived",
    "noreplies",
    "single_user",
    "solved",
    "unsolved",
]


@st.experimental_memo(ttl=TTL, show_spinner=False)
def fetch(path, **query):
    url = urljoin(BASE_URL, path)
    if query:
        query_str = urlencode(query)
        url = "%s?%s" % (url, query_str)
    return requests.get(url)


@st.experimental_memo(ttl=TTL, show_spinner=False)
def fetch_search(q="", page=0):
    resp = fetch("search.json", q=q, page=page)
    data = resp.json()
    if "topics" not in data:
        return None
    search_results = pd.DataFrame(data["topics"])
    search_results["created_at"] = pd.to_datetime(search_results["created_at"])
    search_results["last_posted_at"] = pd.to_datetime(search_results["last_posted_at"])
    return search_results


@st.experimental_memo(ttl=TTL, show_spinner=False)
def get_search_results_as_table(table):
    table = table.copy()
    table = table.drop_duplicates(subset=["id"])
    table["created_at"] = pd.to_datetime(table["created_at"])
    table["last_posted_at"] = pd.to_datetime(table["last_posted_at"])
    return table[
        [
            "title",
            "created_at",
            "last_posted_at",
            "id",
            "posts_count",
            "reply_count",
            "highest_post_number",
            "category_id",
            "has_accepted_answer",
        ]
    ].reset_index(drop=True)


@st.experimental_memo(ttl=TTL, show_spinner=False)
def fetch_all_topic_pages(q=""):
    posts_list = []
    page = 0

    while True:
        batched_posts = fetch_search(q=q, page=page)

        if batched_posts is None:
            break

        posts_list.append(batched_posts)
        page += 1

    posts = pd.concat(posts_list)
    posts_table = get_search_results_as_table(posts)
    return posts_table


@contextmanager
def discourse(top=5, criteria="broad", sortby="relevance", status="any"):
    """Use in a `with` block to execute some code and display
    Streamlit-Discourse topics related to any exception.

    Parameters
    ----------
    top : int
        Number of topics to display. Default is 5.
    criteria : str
        Search criteria. Either 'broad' or 'narrow'. Default is 'broad'.
    sortby : str
        Sort criteria. Either 'relevance', 'views', 'likes', or 'latest_topic'.
        Default is 'relevance'.
    status : str
        Status of Discourse topic. Either 'open', 'closed', 'public', 'archived',
        'noreplies', 'single_user', 'solved', 'unsolved'. Default is 'any'.

    Examples
    --------
    >>> import streamlit as st
    >>> from streamlit_discourse import discourse
    ...
    >>> with discourse():
    >>>     import streamlit as st
    >>>     # Your code that may raise an exception here. E.g.
    >>>     st.what()

    """
    try:
        from streamlit import code, warning, empty, source_util

        placeholder = empty()
        show_code = placeholder.code
        show_warning = placeholder.warning

        def get_initial_indent(lines: Iterable[str]) -> int:
            """Return the indent of the first non-empty line in the list.
            If all lines are empty, return 0.
            """
            for line in lines:
                indent = get_indent(line)
                if indent is not None:
                    return indent

            return 0

        def get_indent(line: str) -> Optional[int]:
            """Get the number of whitespaces at the beginning of the given line.
            If the line is empty, or if it contains just whitespace and a newline,
            return None.
            """
            if _EMPTY_LINE_RE.match(line) is not None:
                return None

            match = _SPACES_RE.match(line)
            return match.end() if match is not None else 0

        try:
            # Get stack frame *before* running the echoed code. The frame's
            # line number will point to the `st.echo` statement we're running.
            frame = traceback.extract_stack()[-3]
            filename, start_line = frame.filename, frame.lineno

            # Read the file containing the source code of the echoed statement.
            with source_util.open_python_file(filename) as source_file:
                source_lines = source_file.readlines()

            # Get the indent of the first line in the echo block, skipping over any
            # empty lines.
            initial_indent = get_initial_indent(source_lines[start_line:])

            # Iterate over the remaining lines in the source file
            # until we find one that's indented less than the rest of the
            # block. That's our end line.
            #
            # Note that this is *not* a perfect strategy, because
            # de-denting is not guaranteed to signal "end of block". (A
            # triple-quoted string might be dedented but still in the
            # echo block, for example.)
            # TODO: rewrite this to parse the AST to get the *actual* end of the block.
            lines_to_display: List[str] = []
            for line in source_lines[start_line:]:
                indent = get_indent(line)
                if indent is not None and indent < initial_indent:
                    break
                lines_to_display.append(line)

            code_string = textwrap.dedent("".join(lines_to_display))

            # Run the echoed code...
            yield

            # And draw the code string to the app!
            # show_code(code_string, "python")

        except FileNotFoundError as err:
            show_warning("Unable to display code. %s" % err)

    except Exception as e:
        etype = type(e).__name__
        str_exception = e
        str_exception_tb = "\n".join(_get_stack_trace_str_list(e))
        get_data(etype, str_exception, str_exception_tb, top, criteria, sortby, status)
        raise e


def get_data(etype, str_exception, str_exception_tb, top, criteria, sortby, status):

    topic_filter = etype

    if criteria == "narrow":
        topic_filter = etype + ": " + str(str_exception)

    if sortby in _ALLOWED_SORTS:
        topic_filter = topic_filter + f" order:{sortby}"

    if status in _ALLOWED_STATUSES:
        topic_filter = topic_filter + f" status:{status}"

    try:
        filtered_topics = fetch_all_topic_pages(q=topic_filter)
    except Exception as e:
        return st.error(
            "[streamlit-discourse] No topics found. Try setting criteria to 'broad'"
        )

    filtered_topics = filtered_topics.head(top)

    st.markdown("##### Related Discourse Topics")
    for topic_id, title in filtered_topics[["id", "title"]].values:
        topic_url = BASE_URL + "/t/" + str(topic_id)
        final_url = f"- [{title}]({topic_url})"
        st.markdown(final_url)
