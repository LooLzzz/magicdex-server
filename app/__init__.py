import dotenv
from fastapi import FastAPI

# dotenv
dotenv.load_dotenv()

# fastapi
app = FastAPI()

# initialize all necessary common modules and values
from .common import *

# start `main.py` !important
from . import main
