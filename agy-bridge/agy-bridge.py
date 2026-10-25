import json, os, re, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
AGY = "/data/home/.local/bin/agy"
WORK = "/tmp/agy-bridge-work"
os.makedirs(WORK, exist_ok=True)
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
DEFAULT_MODEL = "openclaw/default"
AGY_MODELS = [
    ("gemini-4-argon-medium", "Gemini 4 Argon (Medium)"),
    ("gemini-4-argon-high", "Gemini 4 Argon (High)"),
    ("gemini-4-argon-low", "Gemini 4 Argon (Low)"),
    ("gemini-3.8-flash-high", "Gemini 3.8 Flash (High)"),
    ("gemini-3.8-flash-medium", "Gemini 3.8 Flash (Medium)"),
    ("gemini-3.8-flash-low", "Gemini 3.8 Flash (Low)"),
    ("claude-opus-5-5-low", "Claude Opus 5.5 (Low)"),
    ("claude-opus-5-5-medium", "Claude Opus 5.5 (Medium)"),
    ("claude-opus-5-5-high", "Claude Opus 5.5 (High)"),
    ("claude-sonnet-5-5-low", "Claude Sonnet 5.5 (Low)"),
    ("claude-sonnet-5-5-medium", "Claude Sonnet 5.5 (Medium)"),
    ("claude-sonnet-5-5-high", "Claude Sonnet 5.5 (High)"),
    ("gpt-oss-120b-medium", "GPT-OSS 120B (Medium)"),
]
AGY_MODEL_IDS = {m for m, _n in AGY_MODELS}
def resolve_agy_model(requested):
    if not requested or not str(requested).strip():
        return None, None
    v = str(requested).strip()
    if v == DEFAULT_MODEL:
        return None, None
    if v.startswith("magpie/"):
        v = v[len("magpie/"):]
    if v.startswith("agy/"):
        v = v[len("agy/"):]
    if v in AGY_MODEL_IDS:
        return v, None
    return None, "unknown model: " + str(requested)
def run_agy(prompt, agy_model=None):
    full = "You are a helpful chat assistant. Answer in plain text only. Do not read, write, edit, or execute any files and do not call tools." + chr(10) + chr(10) + prompt
    cmd = [AGY]
    if agy_model:
        cmd += ["--model", agy_model]
    cmd += ["-p", full]
    p = subprocess.run(cmd, cwd=WORK, capture_output=True, text=True, timeout=300)
    out = ANSI.sub("", p.stdout or "").strip()
    if not out:
        err = ANSI.sub("", p.stderr or "").strip()
        out = "Error from agy: " + err[-500:] if err else "Error: empty reply from agy"
    return out
def chunk(content, finish, model="openclaw/default"):
    delta = {} if finish else {"content": content}
    d = {"id": "chatcmpl-agy", "object": "chat.completion.chunk", "created": 0, "model": model, "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
    return ("data: " + json.dumps(d, ensure_ascii=False) + chr(10) + chr(10)).encode()
class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write(fmt % args + chr(10))
    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path in ("/healthz", "/v1/healthz"):
            self.send_json(200, {"ok": True, "status": "live"})
        elif self.path in ("/v1/models", "/models"):
            data = [{"id": "openclaw/default", "object": "model", "name": "默认"}]
            for _mid, _name in AGY_MODELS:
                data.append({"id": "agy/" + _mid, "object": "model", "name": _name})
            self.send_json(200, {"object": "list", "data": data})
        else:
            self.send_json(404, {"error": "not found"})
    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            self.send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw.strip():
            self.send_json(400, {"error": "empty request body"})
            return
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self.send_json(400, {"error": "invalid json"})
            return
        msgs = body.get("messages") or []
        if not msgs:
            self.send_json(400, {"error": "no messages"})
            return
        parts = []
        for m in msgs:
            if not isinstance(m, dict):
                continue
            c = m.get("content", "")
            if isinstance(c, list):
                c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
            parts.append(str(m.get("role", "user")) + ": " + str(c))
        prompt = chr(10).join(parts)
        model = body.get("model") or "openclaw/default"
        agy_model, _err = resolve_agy_model(model)
        if _err:
            self.send_json(400, {"error": _err})
            return
        try:
            reply = run_agy(prompt, agy_model)
        except Exception as e:
            reply = "Error running agy: " + str(e)
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            for i in range(0, len(reply), 200):
                self.wfile.write(chunk(reply[i:i+200], None, model))
            self.wfile.write(chunk("", "stop", model))
            self.wfile.write(b"data: [DONE]" + chr(10).encode() + chr(10).encode())
        else:
            self.send_json(200, {"id": "chatcmpl-agy", "object": "chat.completion", "model": model, "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}]})
if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 37289), H).serve_forever()
