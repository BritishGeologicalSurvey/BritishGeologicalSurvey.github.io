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

[ETLHelper](https://pypi.org/project/etlhelper/) is a Python library for reading from and writing to databases that is developed at BGS.
It makes it easy to run a SQL query and transform the results into JSON objects suitable for uploading to an HTTP API.

In some of our projects, we have begun using Python's
[asyncio](https://docs.python.org/3/library/asyncio.html) library to perform
the API uploads concurrently.
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


### Sequential posting with Requests (old way)

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


### Concurrent posting with aiohttp (new way)

```python
def copy_sensors(startdate, enddate):
    """Read sensors from Oracle and post to REST API."""
    with ORACLE_DB.connect('ORACLE_PASSWORD') as conn:
        # chunks is a generator that yields lists of dictionaries
        chunks = iter_chunks(SELECT_SENSORS, conn,
                             parameters={"startdate": startdate,
                                         "enddate": enddate},
                             transform=transform_sensors)

        for chunk in chunks:
            asyncio.run(post_chunk(chunk))
```

```python
async def post_chunk(chunk):
    """Post multiple items to API asynchronously."""
    async with aiohttp.ClientSession() as session:
        # Build list of tasks
        tasks = []
        for item in chunk:
            tasks.append(post_one(item, session))

        # Process tasks in parallel.  An exception in any will be raised.
        await asyncio.gather(*tasks)


async def post_one(item, session):
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

The `asyncio` library is relatively new to Python (since Python 3.4) and has
a reputation of being difficult to understand.
Hopefully this blog post demonstrates how simple it can be and how well it
integrates with ETLHelper's `iter_chunks` function.

If you would like to take a deeper look at `asyncio`, I recommend reading
Real Python's [Async IO in Python](https://realpython.com/async-io-python/)
tutorial.
