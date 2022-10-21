import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# dotenv
dotenv.load_dotenv()

# fastapi
app = FastAPI(docs_url='/docs')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# initialize all necessary common modules and values
from .common import *

# start `main.py` !important
from . import main
