import string
import random
from datetime import datetime
from cassandra_client import session


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    
    while True:
        short_code = "".join(random.choice(chars) for _ in range(length))
        
        # Check if the code already exists in the database
        query = "SELECT short_code FROM short_urls WHERE short_code = %s"
        result = session.execute(query, (short_code,)).one()
        
        # If it doesn't exist, return it
        if not result:
            return short_code

def insert_to_db(short_code, long_url):
    query = """
    INSERT INTO short_urls (short_code, long_url, created_at)
    VALUES (%s, %s, %s)
    USING TTL %s
    """

    session.execute(query, (short_code, long_url, datetime.utcnow(), ttl))

