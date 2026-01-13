import validators
import socket

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from cassandra_client import session
from utils import generate_short_code, insert_to_db


app = FastAPI()
BASE_URL = "http://localhost:8000"


@app.get("/healthcheck")
def healthcheck():
    return "Service is up and running!"


@app.get("/")
def read_root():
    return {"message": "TinyURL Service", "served_by": socket.gethostname()}


@app.post("/shorten")
def shorten_url(long_url: str, expiry_days: int = 7):

    if not validators.url(long_url):
        raise HTTPException(status_code=400, detail="Invalid url")

    short_code = generate_short_code(long_url, length=7)  # 7-character code
    ttl = expiry_days * 24 * 60 * 60
    insert_to_db(short_code, long_url, ttl)
   
    return {"short_url": f"{BASE_URL}/{short_code}"}


@app.get("/{short_code}")
def redirect(short_code: str):

    query = "SELECT long_url FROM short_urls WHERE short_code = %s"
    result = session.execute(query, (short_code,)).one()

    if not result:
        raise HTTPException(status_code=404, detail="ShortURL not found or expired")

    return RedirectResponse(result.long_url)
