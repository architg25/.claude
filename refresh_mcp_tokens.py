#!/usr/bin/env python3
"""Bulk re-authenticate MCP servers for Claude Code.

Reads ~/.claude/.credentials.json and:
1. Refreshes tokens for servers that have refresh_tokens
2. Does full OAuth authorization code flow (with PKCE) for the rest

Usage:
    python ~/.claude/refresh_mcp_tokens.py
    python ~/.claude/refresh_mcp_tokens.py --refresh-only   # skip full OAuth
    python ~/.claude/refresh_mcp_tokens.py --dry-run        # just show status
"""

import base64
import hashlib
import json
import secrets
import shutil
import sys
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event, Thread
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

CREDENTIALS_FILE = Path.home() / ".claude" / ".credentials.json"
DEFAULT_SCOPE = "openid profile email offline_access"
CALLBACK_PORT = 19823
REDIRECT_URI = f"http://127.0.0.1:{CALLBACK_PORT}/callback"
AUTH_TIMEOUT = 60


def load_credentials():
    with open(CREDENTIALS_FILE) as f:
        return json.load(f)


def save_credentials(creds):
    backup = CREDENTIALS_FILE.with_suffix(".json.bak")
    shutil.copy2(CREDENTIALS_FILE, backup)
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(creds, f)
    print(f"  (backed up to {backup.name})")


def discover_metadata(entry):
    """Fetch OAuth discovery metadata for a server if missing."""
    discovery = entry.get("discoveryState", {})
    if discovery.get("authorizationServerMetadata"):
        return  # already have it

    server_url = entry.get("serverUrl", "")
    if not server_url:
        return

    # Try well-known resource metadata to find the auth server
    parsed = urlparse(server_url)
    resource_url = f"{parsed.scheme}://{parsed.netloc}/.well-known/oauth-protected-resource{parsed.path}"

    try:
        resp = urlopen(Request(resource_url, method="GET"), timeout=10)
        resource_meta = json.loads(resp.read())
        auth_servers = resource_meta.get("authorization_servers", [])
        if not auth_servers:
            return

        auth_server = auth_servers[0]
        # Fetch auth server metadata
        well_known = f"{auth_server.rstrip('/')}/.well-known/openid-configuration"
        resp2 = urlopen(Request(well_known, method="GET"), timeout=10)
        server_meta = json.loads(resp2.read())

        # Cache it in the entry
        if "discoveryState" not in entry:
            entry["discoveryState"] = {}
        entry["discoveryState"]["authorizationServerUrl"] = auth_server
        entry["discoveryState"]["resourceMetadataUrl"] = resource_url
        entry["discoveryState"]["resourceMetadata"] = resource_meta
        entry["discoveryState"]["authorizationServerMetadata"] = server_meta
    except Exception:
        pass  # best-effort


def get_endpoint(entry, key, fallback=None):
    metadata = entry.get("discoveryState", {}).get("authorizationServerMetadata", {})
    return metadata.get(key, fallback)


def http_post(url, data):
    """POST form-urlencoded data and return parsed JSON."""
    body = urlencode(data).encode()
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        resp = urlopen(req)
        return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            raise RuntimeError(
                f"HTTP {e.code}: {error_json.get('error_description', error_json.get('error', error_body))}"
            )
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {error_body[:200]}")


def http_post_json(url, data):
    """POST JSON data and return parsed JSON."""
    body = json.dumps(data).encode()
    req = Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        resp = urlopen(req)
        return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {error_body[:200]}")


def refresh_token(entry):
    """Refresh an existing token. Returns expires_in seconds."""
    token_url = get_endpoint(entry, "token_endpoint")
    if not token_url:
        raise RuntimeError("No token endpoint found")

    result = http_post(
        token_url,
        {
            "grant_type": "refresh_token",
            "client_id": entry["clientId"],
            "client_secret": entry["clientSecret"],
            "refresh_token": entry["refreshToken"],
        },
    )

    entry["accessToken"] = result["access_token"]
    if "refresh_token" in result:
        entry["refreshToken"] = result["refresh_token"]
    expires_in = result.get("expires_in", 518400)
    entry["expiresAt"] = int(time.time() * 1000) + (expires_in * 1000)
    return expires_in


def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)[:128]
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return code_verifier, code_challenge


def register_client(entry):
    """Register a new OAuth client via Dynamic Client Registration."""
    register_url = get_endpoint(entry, "registration_endpoint")
    if not register_url:
        raise RuntimeError("No registration endpoint found")

    result = http_post_json(
        register_url,
        {
            "client_name": f"Claude Code MCP - {entry['serverName']}",
            "redirect_uris": [REDIRECT_URI],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
        },
    )

    entry["clientId"] = result["client_id"]
    entry["clientSecret"] = result["client_secret"]
    return result


def authorize_server(entry, callback_server):
    """Full OAuth authorization code flow with PKCE. Returns expires_in seconds."""
    code_verifier, code_challenge = generate_pkce()
    auth_url = get_endpoint(entry, "authorization_endpoint")
    token_url = get_endpoint(entry, "token_endpoint")

    if not auth_url or not token_url:
        raise RuntimeError("Missing auth/token endpoints")

    scope = entry.get("scope") or entry.get("stepUpScope") or DEFAULT_SCOPE

    params = {
        "client_id": entry["clientId"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
        "audience": entry["serverUrl"],
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    full_url = f"{auth_url}?{urlencode(params)}"
    callback_server.reset()
    webbrowser.open(full_url)

    code = callback_server.wait_for_code(timeout=AUTH_TIMEOUT)
    if not code:
        raise TimeoutError("No callback received within timeout")

    result = http_post(
        token_url,
        {
            "grant_type": "authorization_code",
            "client_id": entry["clientId"],
            "client_secret": entry["clientSecret"],
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
    )

    entry["accessToken"] = result["access_token"]
    if "refresh_token" in result:
        entry["refreshToken"] = result["refresh_token"]
    expires_in = result.get("expires_in", 518400)
    entry["expiresAt"] = int(time.time() * 1000) + (expires_in * 1000)
    if "scope" in result:
        entry["scope"] = result["scope"]
    return expires_in


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        if "code" in params:
            self.server._auth_code = params["code"][0]
            self.server._code_event.set()
            self._respond(200, "Authenticated! You can close this tab.")
        elif "error" in params:
            desc = params.get("error_description", params.get("error", ["unknown"]))[0]
            self.server._auth_error = desc
            self.server._code_event.set()
            self._respond(400, f"Error: {desc}")
        else:
            self._respond(404, "Not found")

    def _respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = f"<html><body style='font-family:system-ui;padding:2em'><h2>{message}</h2></body></html>"
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass


class CallbackServer:
    def __init__(self, port):
        self.server = HTTPServer(("127.0.0.1", port), _CallbackHandler)
        self.server._auth_code = None
        self.server._auth_error = None
        self.server._code_event = Event()
        self._thread = Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()

    def reset(self):
        self.server._auth_code = None
        self.server._auth_error = None
        self.server._code_event.clear()

    def wait_for_code(self, timeout=60):
        self.server._code_event.wait(timeout=timeout)
        if self.server._auth_error:
            raise ValueError(self.server._auth_error)
        return self.server._auth_code

    def shutdown(self):
        self.server.shutdown()


def format_expiry(seconds):
    if seconds >= 86400:
        return f"{seconds // 86400}d"
    if seconds >= 3600:
        return f"{seconds // 3600}h"
    return f"{seconds // 60}m"


def show_status(mcp_oauth):
    now_ms = int(time.time() * 1000)
    print(f"{'Server':<35} {'Status':<12} {'Expires':<20} {'Refresh?'}")
    print("-" * 80)
    for key, entry in sorted(
        mcp_oauth.items(), key=lambda x: x[1].get("serverName", "")
    ):
        name = entry.get("serverName", key)
        expires = entry.get("expiresAt", 0)
        has_refresh = bool(entry.get("refreshToken"))
        has_token = bool(entry.get("accessToken")) and expires > 0

        if has_token and expires > now_ms:
            exp_dt = datetime.fromtimestamp(expires / 1000)
            remaining = (expires - now_ms) / 1000
            status = "valid"
            exp_str = f"{exp_dt:%Y-%m-%d %H:%M} ({format_expiry(int(remaining))})"
        elif has_token:
            status = "EXPIRED"
            exp_str = datetime.fromtimestamp(expires / 1000).strftime("%Y-%m-%d %H:%M")
        else:
            status = "NO TOKEN"
            exp_str = "-"

        print(
            f"  {name:<33} {status:<12} {exp_str:<20} {'yes' if has_refresh else 'no'}"
        )
    print()


def main():
    dry_run = "--dry-run" in sys.argv
    refresh_only = "--refresh-only" in sys.argv

    if not CREDENTIALS_FILE.exists():
        print(f"Error: {CREDENTIALS_FILE} not found")
        sys.exit(1)

    creds = load_credentials()
    mcp_oauth = creds.get("mcpOAuth", {})

    if not mcp_oauth:
        print("No MCP servers found in credentials")
        sys.exit(0)

    print(f"Found {len(mcp_oauth)} MCP servers\n")
    show_status(mcp_oauth)

    if dry_run:
        return

    # Split servers by what action they need
    now_ms = int(time.time() * 1000)
    refreshable = {}
    needs_auth = {}
    already_valid = 0
    for key, entry in mcp_oauth.items():
        has_valid_token = (
            entry.get("accessToken") and entry.get("expiresAt", 0) > now_ms
        )
        if has_valid_token:
            already_valid += 1
        elif entry.get("refreshToken"):
            refreshable[key] = entry
        else:
            needs_auth[key] = entry

    if already_valid:
        print(f"Skipping {already_valid} servers with valid tokens")

    # Auto-discover missing metadata
    missing_meta = [
        e
        for e in mcp_oauth.values()
        if not e.get("discoveryState", {}).get("authorizationServerMetadata")
    ]
    if missing_meta:
        print(f"Discovering OAuth metadata for {len(missing_meta)} servers...")
        for entry in missing_meta:
            discover_metadata(entry)
            if entry.get("discoveryState", {}).get("authorizationServerMetadata"):
                print(f"  {entry['serverName']}: discovered")
        print()

    # Phase 1: Refresh existing tokens
    success_count = 0
    if refreshable:
        print(f"Phase 1: Refreshing {len(refreshable)} tokens...")
        for key, entry in refreshable.items():
            name = entry.get("serverName", key)
            try:
                expires_in = refresh_token(entry)
                print(f"  {name}: refreshed (expires in {format_expiry(expires_in)})")
                success_count += 1
            except Exception as e:
                print(f"  {name}: FAILED ({e})")
                needs_auth[key] = entry
        print()

    # Phase 2: Full OAuth
    if needs_auth and not refresh_only:
        print(f"Phase 2: Authenticating {len(needs_auth)} servers via browser...")
        print(f"  Callback server on {REDIRECT_URI}")
        print(
            f"  Your browser will open for each server. SSO should auto-approve most.\n"
        )

        try:
            callback = CallbackServer(CALLBACK_PORT)
        except OSError as e:
            print(
                f"  Error: Could not start callback server on port {CALLBACK_PORT}: {e}"
            )
            print(f"  Try closing any process using that port and retry.")
            save_credentials(creds)
            sys.exit(1)

        try:
            for key, entry in needs_auth.items():
                name = entry.get("serverName", key)
                has_discovery = bool(
                    entry.get("discoveryState", {}).get("authorizationServerMetadata")
                )

                if not has_discovery:
                    print(f"  {name}: skipped (no OAuth discovery metadata)")
                    continue

                try:
                    # Re-register client so we control the redirect_uri
                    print(f"  {name}: registering client...", end=" ", flush=True)
                    register_client(entry)
                    print("opening browser...", end=" ", flush=True)
                    expires_in = authorize_server(entry, callback)
                    print(f"done (expires in {format_expiry(expires_in)})")
                    success_count += 1
                except TimeoutError:
                    print("TIMEOUT (skipped)")
                except KeyboardInterrupt:
                    print("\nInterrupted. Saving progress...")
                    break
                except Exception as e:
                    print(f"FAILED ({e})")
        finally:
            callback.shutdown()
        print()
    elif needs_auth and refresh_only:
        print(
            f"Skipping {len(needs_auth)} servers without refresh tokens (--refresh-only)"
        )
        print()

    # Save
    save_credentials(creds)

    # Summary
    now_ms = int(time.time() * 1000)
    authed = sum(
        1
        for e in mcp_oauth.values()
        if e.get("accessToken") and e.get("expiresAt", 0) > now_ms
    )
    print(f"Done! {authed}/{len(mcp_oauth)} servers have valid tokens.")


if __name__ == "__main__":
    main()
