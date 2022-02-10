# streamlit-discourse
Streamlit component to display [Streamlit-Discourse](https://discuss.streamlit.io/) topics related to any exception.

## Installation

```bash
pip install git+https://github.com/snehankekre/streamlit-discourse
```

## Docs

To view the docstring, import Streamlit and the component and call `st.help(discourse)`.

```markdown
streamlit_discourse.discourse(top=5, criteria='broad', sortby='relevance', status='any')
Use in a `with` block to execute some code and display 
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

```

## Usage

```python
import streamlit as st
from streamlit_discourse import discourse

with discourse():
    import streamlit as st
    # Your code that may raise an exception here. E.g.
    import numpy as np
    np.rounds()
```
![Example](streamlit-discourse.gif)
