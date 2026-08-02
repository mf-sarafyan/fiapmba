"""Teste programatico do agente via API run_sse (requer adk web rodando)."""
import json
import sys
import time
import uuid

import requests

APP = "quantum_finance_advisor"
BASE = "http://127.0.0.1:8000"
USER = "debug-user"
SESSION = str(uuid.uuid4())
LOG_PATH = __file__.replace("test_run_sse.py", "..\\debug-86d071.log").replace("\\scripts\\..\\", "\\")


def dbg(msg: str, data: dict, hid: str) -> None:
    import pathlib
    p = pathlib.Path(__file__).resolve().parents[1] / "debug-86d071.log"
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "sessionId": "86d071", "timestamp": int(time.time() * 1000),
            "location": "test_run_sse.py", "message": msg, "data": data,
            "hypothesisId": hid, "runId": "run_sse",
        }, ensure_ascii=False) + "\n")


def main() -> int:
    # criar sessao
    r = requests.post(
        f"{BASE}/apps/{APP}/users/{USER}/sessions",
        json={"sessionId": SESSION},
        timeout=10,
    )
    dbg("session_create", {"status": r.status_code, "body": r.text[:500]}, "E")
    if r.status_code not in (200, 201):
        print(f"FALHA criar sessao: {r.status_code} {r.text}")
        return 1

    payload = {
        "appName": APP,
        "userId": USER,
        "sessionId": SESSION,
        "newMessage": {
            "role": "user",
            "parts": [{"text": "Ola, quero comecar a investir"}],
        },
        "streaming": False,
    }
    r = requests.post(f"{BASE}/run_sse", json=payload, timeout=120)
    dbg("run_sse", {"status": r.status_code, "body": r.text[:2000]}, "A")
    print(f"HTTP {r.status_code}")
    print(r.text[:3000])
    if "error" in r.text.lower():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
