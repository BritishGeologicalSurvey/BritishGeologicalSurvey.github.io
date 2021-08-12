---
title:  "Fast API creation with FastAPI"
author: Colin Blackburn
categories:
  - API Development
tags:
  - API
  - Python
---

The BGS runs a number of web services using technologies such as ColdFusion and PHP. These are becoming increasingly difficult to maintain or extend through lack of expertise, but also because these systems combine front-end and back-end functionality. When replacement or extension is needed it is generally better to develop separate APIs that can be used by loosely-coupled front-ends. To this end, the Python developers at BGS have tested a number of frameworks used to create APIs: `falcon`, `flask` and `hug`, before landing on [FastAPI](https://fastapi.tiangolo.com/).

### SADC and Palaeosaurus

The first projects to use FastAPI were the Palaeosaurus and [SADC Groundwater Literature Archive](http://sadc-gla.org/SADC/) APIs. Here's how easy it is to create an end-point and JSON response:

```python
from enum import Enum
from fastapi import APIRouter, FastAPI, Path, Request
from pydantic import BaseModel, Field

# Use Python classes and pydantic to define the JSON response schema
class Country(BaseModel):
    code: str = Field(..., example="ZA")
    name: str = Field(..., example="South Africa")

class MinimalResponse(BaseModel):
    msg: str = Field(..., example="Example response")
    type: str = Field(..., example="success")
    self: str = Field(..., example="http://example.com/apis/query")

class CountryResponse(MinimalResponse):
    data: List[Country] = None

# Use fastapi to define the path schema
class ArchiveName(str, Enum):
    SADC = "SADC"
    AGLA = "AGLA"

archive_path = Path(
    ..., title='Archive name',
    description='Archive name to run queries against',
    example='SADC')

code_path = Path(
    ..., title='Country code',
    description='The two-letter code for a country',
    regex='^[A-Z]{2}$',
    example='BW')

router = APIRouter()

# Use a python decorator to define the path
@router.get(
    '/african-groundwater/{archive}/country/{code}',
    response_model=CountryResponse
)
def country_by_code(
        archive: ArchiveName = archive_path,
        code: str = code_path,
        request: Request = None):
    # Get the populated CountryResponse object
    rsp = _get_country_by_code_response(code)
    rsp.self = str(request.url)
    return rsp

# Create the app
app = FastAPI(docs_url='/african-groundwater/docs',
              openapi_url='/african-groundwater/openapi.json')

# Add a route
app.include_router(country_by_code.router)

# And that's it!
```

As well as a working API that chacks the parameters - that enum and regex - FastAPI also generates Swagger docs and an openAPI schema.

![Image of Swagger docs](../../assets/images/2021-08-11-fast-apis/swagger.png)

Need to add CORS? Just use the CORS middleware:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
```
