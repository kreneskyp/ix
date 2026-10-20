Web search
==========

The **Self Ask with Search Agent** uses `Parallel Search MCP
<https://docs.parallel.ai/integrations/mcp/search-mcp>`_ when no search tool is
connected. Search runs in Fast mode and needs no Parallel account or API key.
Connect an LLM to the agent, then send your question in the chat.

A connected tool takes precedence. Self Ask requires exactly one tool named
``Intermediate Answer``. Existing tool connections and credentials keep working;
a failed configured provider does not trigger a switch to Parallel.

To require an explicitly connected search tool, turn off **Enable default
search** on the Self Ask agent. In Python, pass ``default_search=False``.
An explicit ``tools=[]`` also prevents default search. As before, Self Ask cannot
run without a usable search tool. Other agent types receive only the tools you
connect to them.

Search and fetch components
---------------------------

After updating IX, run ``./manage.py import_langchain`` (or ``make dev_setup``)
to refresh component definitions. The editor offers:

* **Parallel Search**: accepts a search query and returns excerpts with source
  URLs.
* **Parallel Fetch**: accepts one HTTP or HTTPS URL and returns page text with
  its source URL.

Connect these components as tools to an agent or use them in a runnable flow.
Each component has a **Timeout (sec)** setting, defaulting to 30 seconds per HTTP
operation. Network failures, service errors, and rate limits surface as tool
errors. The free service has usage limits; it does not require credentials.

IX uses the chat's opaque UUID across related searches, fetches, follow-up turns,
and retries. A new chat gets a different ID. Tasks outside a chat use their task
UUID. For Python use, pass the same ``IxContext`` to search and fetch in one
conversation. Without a context, each constructed tool represents one standalone
research run; reuse it for follow-up calls and construct a new one for a new run.

.. code-block:: python

    from ix.tools.parallel import get_parallel_search, get_parallel_fetch

    # context is the current conversation's IxContext.
    search = get_parallel_search(context=context)
    fetch = get_parallel_fetch(context=context)
    excerpts = await search.ainvoke("IX autonomous agent platform")
    page = await fetch.ainvoke("https://github.com/kreneskyp/ix")
