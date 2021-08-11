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
print('tbc')
```


### Concurrent posting with aiohttp (new way)

```python
print('tbc')
```

## Conclusion

The `asyncio` library is relatively new to Python (since Python 3.4) and has
a reputation of being difficult to understand.
Hopefully this blog post demonstrates how simple it can be and how well it
integrates with ETLHelper's `iter_chunks` function.

If you would like to take a deeper look at `asyncio`, I recommend reading
Real Python's [Async IO in Python](https://realpython.com/async-io-python/)
tutorial.
