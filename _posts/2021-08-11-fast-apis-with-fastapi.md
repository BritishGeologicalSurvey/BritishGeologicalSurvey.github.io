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

The first projects to use FastAPI were the Palaeosaurus and [SADC Groundwater Literature Archive](http://sadc-gla.org/SADC/) APIs. Here's how easy it is to create a single end-point and JSON response:

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
    ..., # Required parameter
    title='Archive name',
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

As well as a working API that checks the parameters - enum and regex up above - FastAPI also automatically generates Swagger docs and an openAPI schema using the FastAPI Path classes and Pydantic model classes.

![Image of Swagger docs](../../assets/images/2021-08-11-fast-apis/swagger.png)

Of course it can handle query parameters as well as path parameters:

```python
from fastapi import Query, Request

collector_query = Query(
    None, # Optional parameter
    title='', description='', example='SURVEY?')

locality_query = Query(
    None, title='The Locality', description='', example='Bellcraig Burn')

limit_query = Query(
    default=1000, # Default value if none is given
    title='Limit', description='The pagination limit')

offset_query = Query(
    default=0, title='Offset', description='The pagination offset')

@router.get(
    get_config().BASE_PATH + '/specimens',
    response_model=SpecimenResponse)
def get_specimens(
    request: Request, collector: str = collector_query,
    locality: str = locality_query, limit: int = limit_query,
    offset: int = offset_query):

    request_params = set(request.query_params.keys())
    # ... validate the parameters and make the search
    return response
```

Need to add CORS? Use the CORS middleware:

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

Need to handle exceptions? Use the exception handler decorator:

```python
    @app.exception_handler(DatabaseError)
    async def database_exception(request: Request, exc: DatabaseError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(exc.response())
        )
```

Need logging? Use the `http` middleware to intercept the call:

```python
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Called by {request.client.host}")
        logger.debug(f"Request headers: {request.headers}")
        start_time = time.time()
        response = await call_next(request)
        call_time = int((time.time() - start_time) * 1000)
        logger.debug(f"Request status: {response.status_code}, time: {call_time} ms")
        return response
```

Need log ins?

```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

# Create a route to get access token using OAuth2 form
@router.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    authenticate_user(form_data.username, form_data.password)
    token = create_access_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}

# Check whether current token is valid, return user is it is
def get_current_user(token: str = Depends(oauth2_scheme)):
    # ...
    return user

# This route Depends on get_current_user to check the token
@router.get('/item/id/{item_id}', response_model=ItemResponse)
def get_item_by_id(request: Request, item_id: str = item_id_path,
                   current_user: User = Depends(get_current_user)):
    # ...
    return response
```


```python
from fastapi import Body, Request

@router.put('/mailing/update/{mailing_id}', response_model=MailingsResponse)
def update_mailing_record(
    request: Request, mailing: dict = Body(...),
    mailing_id: int = mailing_id_path, apikey: str = apikey_query):

    validate_body(mailing_id, mailing)
    # Query database
    try:
        has_access(apikey=apikey, access='UPDATE')
    except AccessError as e:
        logging.error(e)
        raise HTTPException(status_code=401, detail=e.detail)
    # ...
    return response

```
