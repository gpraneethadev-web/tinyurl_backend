import string
import random
import hashlib
from datetime import datetime
from cassandra_client import session

def to_base_62(deci):
    """Convert decimal number to base-62 string"""
    s = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    hash_str = ''
    while deci > 0:
        hash_str = s[deci % 62] + hash_str
        deci //= 62 
    return hash_str


def generate_short_code(long_url, length=7):
    """Generate deterministic 7-character short code from URL hash (no race condition)"""
    # Hash the URL to get a consistent code
    hash_obj = hashlib.sha256(long_url.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # Convert to base-62 and take first 'length' characters
    short_code = to_base_62(hash_int)[:length]
    
    # Pad with zeros if needed
    if len(short_code) < length:
        short_code = short_code.ljust(length, '0')
    
    return short_code


def insert_to_db(short_code, long_url, ttl):
    """Insert short URL mapping into database"""
    query = """
    INSERT INTO short_urls (short_code, long_url, created_at)
    VALUES (%s, %s, %s)
    USING TTL %s
    """
    session.execute(query, (short_code, long_url, datetime.utcnow(), ttl))

