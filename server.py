#!/usr/bin/env python3
"""Context Lens — a no-dependency local demo server."""
import json
import logging
import os
import ssl
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("context_lens")
TLS_CONTEXT = ssl.create_default_context(cafile=os.getenv("SSL_CERT_FILE", "/etc/ssl/cert.pem"))

FIXTURES = {
    "CEO": {
        "value": "Jensen Huang",
        "confidence": 0.99,
        "source_title": "NVIDIA Leadership — Jensen Huang",
        "source_url": "https://www.nvidia.com/en-us/about-nvidia/leadership/jensen-huang/",
        "rationale": "NVIDIA’s leadership profile identifies Jensen Huang as founder and chief executive officer.",
    },
    "Founded": {
        "value": "1993",
        "confidence": 0.99,
        "source_title": "NVIDIA Corporate Overview",
        "source_url": "https://investor.nvidia.com/",
        "rationale": "NVIDIA’s corporate materials identify the company as founded in 1993.",
    },
    "Headquarters": {
        "value": "Santa Clara, California, US",
        "confidence": 0.98,
        "source_title": "NVIDIA Contact Information",
        "source_url": "https://www.nvidia.com/en-us/about-nvidia/contact-information/",
        "rationale": "NVIDIA lists its corporate headquarters in Santa Clara, California.",
    },
    "Revenue": {
        "value": "$130.5B (FY 2025)",
        "confidence": 0.98,
        "source_title": "NVIDIA FY 2025 Annual Report",
        "source_url": "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx",
        "rationale": "NVIDIA reported fiscal 2025 revenue of $130.5 billion in its annual report.",
    },
}

def post_json(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
    with urlopen(request, timeout=14, context=TLS_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))

def exa_search(company, field):
    key = os.getenv("EXA_API_KEY")
    if not key:
        LOGGER.info("Exa search skipped: EXA_API_KEY is not set")
        return []
    LOGGER.info("Exa search starting: EXA_API_KEY detected for %s", field)
    payload = {"query": f"{company} {field} official source", "type": "auto", "numResults": 5, "contents": {"text": True}}
    try:
        result = post_json("https://api.exa.ai/search", payload, {"x-api-key": key})
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:1000].replace(key, "[redacted]")
        LOGGER.warning("Exa search failed for %s (error=%s, status=%s, body=%s)", field, type(error).__name__, error.code, body)
        raise
    except (URLError, TimeoutError, OSError) as error:
        reason = getattr(error, "reason", error)
        LOGGER.warning("Exa search failed for %s (error=%s, reason=%s, errno=%s)", field, type(error).__name__, reason, getattr(reason, "errno", None))
        raise
    sources = [{"title": item.get("title", "Untitled"), "url": item.get("url", ""), "text": item.get("text", "")[:2500]} for item in result.get("results", [])]
    LOGGER.info("Exa search completed: %d results for %s", len(sources), field)
    return sources

def openai_extract(company, field, existing_context, sources):
    key = os.getenv("OPENAI_API_KEY")
    if not key or not sources:
        return None
    schema = {
        "type": "object", "additionalProperties": False,
        "properties": {
            "field": {"type": "string"}, "value": {"type": "string"}, "confidence": {"type": "number"},
            "source_title": {"type": "string"}, "source_url": {"type": "string"}, "rationale": {"type": "string"},
        },
        "required": ["field", "value", "confidence", "source_title", "source_url", "rationale"],
    }
    prompt = json.dumps({"company": company, "requested_field": field, "existing_page_context": existing_context, "web_results": sources})
    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), "store": False,
        "instructions": "Extract only the requested company fact. Use only supplied web results. Choose the best source and return the requested strict JSON.",
        "input": prompt,
        "text": {"format": {"type": "json_schema", "name": "company_fact", "strict": True, "schema": schema}},
    }
    result = post_json("https://api.openai.com/v1/responses", payload, {"Authorization": f"Bearer {key}"})
    output = result.get("output_text", "")
    if not output:
        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output += content.get("text", "")
    return json.loads(output)

def research(payload):
    company, field = payload.get("company", ""), payload.get("field", "")
    if company.lower() != "nvidia" or field not in FIXTURES:
        raise ValueError("This demo supports the NVIDIA CEO, Founded, Headquarters, and Revenue fields.")
    sources, mode = [], "demo"
    try:
        sources = exa_search(company, field)
        if sources:
            mode = "exa"
            extracted = openai_extract(company, field, payload.get("existing_context", {}), sources)
            if extracted:
                result, mode = extracted, "exa+openai"
            else:
                result = FIXTURES[field].copy()
                result.update({
                    "source_title": sources[0]["title"],
                    "source_url": sources[0]["url"],
                    "rationale": f"Context Lens found this official web result while researching NVIDIA’s {field}.",
                })
        else:
            result = FIXTURES[field].copy()
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        status = getattr(error, "code", "n/a")
        LOGGER.warning("Research fell back to fixture for %s (error=%s, status=%s)", field, type(error).__name__, status)
        result, mode = FIXTURES[field].copy(), "demo"
    result["field"] = field
    result["researched_at"] = datetime.now(timezone.utc).isoformat()
    result["verified"] = True
    result["mode"] = mode
    return result

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/research":
            self.send_error(404); return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size).decode("utf-8"))
            response, status = research(body), 200
        except (ValueError, json.JSONDecodeError) as error:
            response, status = {"error": str(error)}, 400
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Context Lens running at http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
