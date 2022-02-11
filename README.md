# streamlit-forum
Streamlit component to display topics from Streamlit's [community forum](https://discuss.streamlit.io/) related to any exception.

## Installation

```bash
pip install git+https://github.com/snehankekre/streamlit-forum
```

## Usage

```python
import streamlit as st
from streamlit_forum import forum

with forum():
    import streamlit as st
    # Your code that may raise an exception here. E.g.
    0/0
```

https://user-images.githubusercontent.com/20672874/153559386-02d1eee9-267e-4438-b760-e853244f5e63.mp4

## Docs

To view the docstring, import Streamlit and the component and call `st.help(forum)`.

```markdown
streamlit_forum.forum(top=5, criteria='broad', sortby='relevance', status='any')
Use in a `with` block to execute some code and display 
topics from Streamlit's community forum related to any exception.

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
    Status of forum topic. Either 'open', 'closed', 'public', 'archived',
    'noreplies', 'single_user', 'solved', 'unsolved'. Default is 'any'.

Examples
--------
>>> import streamlit as st
>>> from streamlit_forum import forum
...
>>> with forum():
>>>     import streamlit as st
>>>     # Your code that may raise an exception here. E.g.
>>>     0/0

```
