import streamlit as st

from contextlib import contextmanager
import re
from urllib.parse import urljoin, urlencode
import pandas as pd
import requests

_BASE_URL = "https://discuss.streamlit.io"
_TTL = 1 * 60 * 60  # 1 hour

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


@st.experimental_memo(ttl=_TTL, show_spinner=False)
def _fetch(path, **query):
    url = urljoin(_BASE_URL, path)
    if query:
        query_str = urlencode(query)
        url = "%s?%s" % (url, query_str)
    return requests.get(url)


@st.experimental_memo(ttl=_TTL, show_spinner=False)
def _fetch_search(q="", page=0):
    resp = _fetch("search.json", q=q, page=page)
    data = resp.json()
    if "topics" not in data:
        return None
    search_results = pd.DataFrame(data["topics"])
    search_results["created_at"] = pd.to_datetime(search_results["created_at"])
    search_results["last_posted_at"] = pd.to_datetime(search_results["last_posted_at"])
    return search_results


@st.experimental_memo(ttl=_TTL, show_spinner=False)
def _get_search_results_as_table(table):
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


@st.experimental_memo(ttl=_TTL, show_spinner=False)
def _fetch_all_topic_pages(q=""):
    posts_list = []
    page = 0

    while True:
        batched_posts = _fetch_search(q=q, page=page)

        if batched_posts is None:
            break

        posts_list.append(batched_posts)
        page += 1

    posts = pd.concat(posts_list)
    posts_table = _get_search_results_as_table(posts)
    return posts_table


def _get_data(etype, str_exception, top, criteria, sortby, status):

    # If the criteria is 'broad', search for topics with only
    # the exception name. e.g. 'ValueError'
    query = etype

    # Search for topics with the exception name and the exception
    # message. e.g. 'ValueError: invalid literal for int() with base 10: 'foo'
    if criteria == "narrow":
        query = query + ": " + str(str_exception)

    # TODO: Improve above search logic

    # See: https://docs.discourse.org/#tag/Search    
    if sortby in _ALLOWED_SORTS:
        query = query + f" order:{sortby}"

    if status in _ALLOWED_STATUSES:
        query = query + f" status:{status}"

    try:
        result = _fetch_all_topic_pages(q=query)
    except Exception as e:
        return st.error(
            "[streamlit-discourse] No topics found. Try setting criteria to 'broad'"
        )

    result = result.head(top)

    return _display_result(result)


def _display_result(result):
    st.markdown("##### Related Discourse Topics")
    for topic_id, title in result[["id", "title"]].values:
        topic_url = _BASE_URL + "/t/" + str(topic_id)
        topic_url = f"- [{title}]({topic_url})"
        st.markdown(topic_url)


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
    >>>     0/0

    """
    try:
        # Run the code in the `with` block.
        yield

    except Exception as e:
        etype = type(e).__name__  # e.g. 'ValueError', 'TypeError'
        str_exception = e  # e.g. invalid literal for int() with base 10: 'foo'

        _get_data(etype, str_exception, top, criteria, sortby, status)

        # If the code in the `with` block raises an exception,
        # re-raise it so that the user sees the error.
        raise e
