---
title:  "Speeding up ETLHelper's API transfers with asyncio"
author: Dr John A Stevenson
categories:
  - open-source
tags:
  - Python
  - asyncio
  - database
  - etlhelper
---

[ETLHelper](https://pypi.org/project/etlhelper/) is a Python library developed at BGS for reading from and writing to databases.
It makes it easy to run a SQL query and transform the results into JSON objects suitable for uploading to an HTTP API.

In some of our projects, we have begun to use Python's asynchronous capabilities to perform
concurrent API uploads.
As a result, we have seen speed increases of up to 10x compared to
our previous method of posting data sequentially.

This post compares the two methods and shows how simple the `asyncio` code can
be.


## Comparison of sequential and concurrent API upload code

The code below is taken from the
[Recipes](https://github.com/BritishGeologicalSurvey/etlhelper#recipes) section
of the ETLHelper documentation, which includes an [example ETL
script](https://github.com/BritishGeologicalSurvey/etlhelper#database-to-api--nosql-copy-etl-script-template)
to transfer data from an Oracle database to an ElasticSearch API.
The script originally described posting items sequentially using the
[Requests](https://docs.python-requests.org/en/master/) library and has now been [updated](https://github.com/BritishGeologicalSurvey/etlhelper/compare/13cd104..f7cfc0b) to use concurrent processing with the [aiohttp](https://docs.aiohttp.org/en/stable/) library.

Only the most relevant parts of code are shown here - see the [ETLHelper
documentation](https://realpython.com/introduction-to-python-generators/) for full details.


### Sequential posting with Requests

ETLHelper provides the `iter_rows` function that returns
a [generator](https://realpython.com/introduction-to-python-generators/) item
that yields a new result from the database with each iteration.
Results are fetched from the database only as required instead of all being loaded into
memory first.
This makes it suitable for transferring large quantities of data.

In this case, the `iter_rows` call runs a SQL query (`SELECT_SENSORS`) against
the database and applies a transform function (`transform_sensors`) to convert
the result into a Python dictionary that can be easily converted to JSON.  The
resulting item is posted to the API.


```python
def copy_sensors(startdate, enddate):
    """Read sensors from Oracle and post to REST API."""
    with ORACLE_DB.connect('ORACLE_PASSWORD') as conn:
        # Iterate over rows individually
        for item in iter_rows(SELECT_SENSORS, conn,
                              parameters={"startdate": startdate,
                                          "enddate": enddate},
                              transform=transform_sensors):
            post_item(item)
```

[Requests](https://docs.python-requests.org/en/latest/) is an HTTP library for Python that can be used to communicate with APIs.
The `post_item` function uses Requests to post the item.
It also raises an exception if something goes wrong.

```python
def post_item(item):
    """Post a single item to API."""
    # Post data to API
    response = requests.post(BASE_URL + 'sensors/_doc', headers=HEADERS,
			     data=json.dumps(item))

    # Check for failed rows
    if response.status_code >= 400:
	logger.error('The following item failed: %s\nError message:\n(%s)',
		     item, response.text)
	response.raise_for_status()
```

This code is very simple, but it can be slow as the Python interpreter has to
wait for a response from the API before it can proceed to the next item.


### Concurrent posting with aiohttp and asyncio

The [aiohttp](https://docs.aiohttp.org/en/stable/) library is similar to Requests, but it is based on Python's [asyncio](https://docs.python.org/3/library/asyncio.html) library for asynchronous execution.
This provides an efficient way to make multiple concurrent API calls.

In the concurrent version, we use the `iter_chunks` to pull the data from the
database.
This returns a generator that yields a list of results (5000 at a time by
default) with each iteration.
The `post_chunk` function posts the results in each chunk concurrently.
Because `post_chunk` is an asynchronous function, it needs to be called by `asyncio.run()`.
Otherwise, the `copy_sensors` function is very similar to before.


```python
def copy_sensors(startdate, enddate):
    """Read sensors from Oracle and post to REST API."""
    with ORACLE_DB.connect('ORACLE_PASSWORD') as conn:
        # iterate over chunks of rows
        for chunk in iter_chunks(SELECT_SENSORS, conn,
                                 parameters={"startdate": startdate,
                                             "enddate": enddate},
                                 transform=transform_sensors)
            asyncio.run(post_chunk(chunk))
```

Two functions are required for asynchronously posting to the API - one to post a single item
and another call the first concurrently for all of our items.

`post_chunk` handles the concurrency.
It builds a list of tasks, one for each item, then calls `asyncio.gather()` to execute them asynchronously (and collect
the results if required).
An `aiohttp.ClientSession` allows the same connection to the server to be reused for each item in the chunk.

```python
async def post_chunk(chunk):
    """Post multiple items to API asynchronously."""
    async with aiohttp.ClientSession() as session:
        # Build list of tasks
        tasks = []
        for item in chunk:
            tasks.append(post_item(item, session))

        # Process tasks in parallel.  An exception in any will be raised.
        await asyncio.gather(*tasks)
```

The `post_item` function is similar to the Requests version.
The main differences are the use of _await_ keywords and that `response.text`
is an awaitable function here, whereas it is an attribute in Requests.
Also, it is essential to log any error information before raising an
exception if something goes wrong.
Otherwise, it is not possible to access all the state information for the [awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables) `response` via a debugger.

```python
async def post_item(item, session):
    """Post a single item to API using existing aiohttp Session."""
    # Post the item
    response = await session.post(BASE_URL + 'sensors/_doc', headers=HEADERS,
                                  data=json.dumps(item))

    # Log responses before throwing errors because error info is not included
    # in generated Exceptions and so cannot otherwise be seen for debugging.
    if response.status >= 400:
        response_text = await response.text()
        logger.error('The following item failed: %s\nError message:\n(%s)',
                     item, response_text)
        await response.raise_for_status()
```

## Conclusion

Asynchronous frameworks based on `asyncio` library are relatively new to Python (since Python 3.4) and have
a reputation of being difficult to understand.
Hopefully this blog post demonstrates how `aiohttp` can be used to make concurrent API requests and how well it
integrates with ETLHelper's `iter_chunks` function.

If you would like to take a deeper look at `asyncio`, I recommend reading
Real Python's [Async IO in Python](https://realpython.com/async-io-python/)
tutorial.
