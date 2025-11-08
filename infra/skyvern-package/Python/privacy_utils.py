import os
import re
import hashlib

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}')
APIKEY_RE = re.compile(r'\b(?:sk-|ghp_)[A-Za-z0-9-_]{16,}\b')
CARD_RE = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

def redact(text: str | None) -> str | None:
    if not text:
        return text
    t = EMAIL_RE.sub('[REDACTED:email]', text)
    t = APIKEY_RE.sub('[REDACTED:apikey]', t)
    t = CARD_RE.sub('[REDACTED:number]', t)
    return t[:4000]

def sha256(x: str) -> str:
    return hashlib.sha256(x.encode('utf-8')).hexdigest()

def should_keep_raw_prompts() -> bool:
    return os.getenv('KEEP_RAW_PROMPTS', 'false').lower() == 'true'

def ttl_days(key: str, fallback: int) -> int:
    try:
        return int(os.getenv(key, str(fallback)))
    except ValueError:
        return fallback
