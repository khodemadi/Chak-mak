"""Check any API against the contract.  Usage: python mock-api/validate.py [base_url]"""
import json
import re
import sys
import urllib.error
import urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
problems = []


def get(path):
    try:
        with urllib.request.urlopen(base + path, timeout=10) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


status, body = get("/api/messages?limit=20")
if status != 200:
    problems.append(f"status {status}, expected 200")
else:
    if body.get("version") != 1:
        problems.append("version must be 1")
    msgs = body.get("messages")
    if not isinstance(msgs, list):
        problems.append("messages must be a list")
        msgs = []
    if body.get("count") != len(msgs):
        problems.append("count != len(messages)")
    if len(msgs) > 20:
        problems.append("more than limit messages returned")
    if not DATE.match(str(body.get("fetched_at", ""))):
        problems.append("fetched_at must be ISO 8601 UTC with Z")
    types = {"id": int, "channel": str, "sender": str, "text": str, "date": str, "has_media": bool}
    for i, m in enumerate(msgs):
        for k, t in types.items():
            if k not in m:
                problems.append(f"messages[{i}] missing '{k}'")
            elif not isinstance(m[k], t) or (t is int and isinstance(m[k], bool)):
                problems.append(f"messages[{i}].{k} must be {t.__name__}")
        if isinstance(m.get("date"), str) and not DATE.match(m["date"]):
            problems.append(f"messages[{i}].date bad format: {m['date']}")
    dates = [m.get("date", "") for m in msgs]
    if dates != sorted(dates, reverse=True):
        problems.append("messages must be newest first")

status, body = get("/api/messages?limit=0")
if status != 400 or body.get("error", {}).get("code") != "bad_limit":
    problems.append("limit=0 must give 400 with error.code=bad_limit")

if problems:
    print("FAIL")
    print("\n".join(" - " + p for p in problems))
    sys.exit(1)
print("OK: API matches contract v1")
