"""Full browser/HTTP/PostgreSQL and real WebSocket upgrade smoke in isolated CI.

Does not stream audio to Gemini. Tests HTTP, persisted candidate invites and
both accepted/rejected coverage WS frames, plus rejected audio WS frames.
"""
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse, quote

from playwright.sync_api import sync_playwright, expect

API_BASE = "http://127.0.0.1:3001/api/v1"
WEB_BASE = "http://127.0.0.1:5173"
FIXTURE = Path(tempfile.gettempdir()) / "quality-net-browser-fixture.json"


def ws_message(page, url, payload):
    # Actual browser-created WebSocket: onopen proves HTTP 101 upgrade.
    return page.evaluate(
        """async ({url, payload}) => {
            return await new Promise((resolve) => {
                let opened = false;
                let finished = false;
                const messages = [];
                const socket = new WebSocket(url);
                const stop = (reason) => {
                    if (finished) return;
                    finished = true;
                    clearTimeout(timer);
                    try { socket.close(); } catch (_) {}
                    resolve({opened, reason, messages});
                };
                const timer = setTimeout(() => stop('timeout'), 8000);
                socket.onopen = () => {
                    opened = true;
                    socket.send(JSON.stringify(payload));
                };
                socket.onerror = () => stop('socket-error');
                socket.onclose = () => stop('closed');
                socket.onmessage = (event) => {
                    let value;
                    try { value = JSON.parse(event.data); } catch (_) { return; }
                    messages.push(value.type === 'error'
                        ? {type: 'error', code: value.code}
                        : {type: value.type, status: value.status});
                    if (value.type === 'error' || value.type === 'coverage_update') {
                        stop('received');
                    }
                };
            });
        }""",
        {"url": url, "payload": payload},
    )


def main():
    if os.environ.get("RAILS_ENV") != "test":
        raise RuntimeError("Refusing browser E2E against a non-test Rails environment")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(base_url=WEB_BASE, permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        try:
            # Browser genuinely submits the login form and loads Rails/PostgreSQL-backed UI.
            page.goto("/login", wait_until="domcontentloaded")
            page.get_by_label("Email").fill(data["email"])
            page.get_by_label("Password").fill(data["password"])
            page.get_by_label("Organization code (optional)").fill(data["scheme"])
            page.get_by_role("button", name="Sign in").click()
            expect(page.get_by_role("heading", name="Assessments")).to_be_visible(timeout=20000)
            expect(page.get_by_text("E2E Browser Assessment")).to_be_visible()
            assert page.url.endswith("/assessments"), "BROWSER-DB-01: login did not navigate"

            # Create candidate invite by clicking the actual React dialog, not a test API shortcut.
            page.get_by_text("E2E Browser Assessment").click()
            expect(page.get_by_role("button", name="Invite Candidate")).to_be_visible()
            page.get_by_role("button", name="Invite Candidate").click()
            page.get_by_label("Candidate name").fill("Synthetic Browser Guest")
            page.get_by_role("button", name="Create Link").click()
            expect(page.get_by_text("Synthetic Browser Guest").first).to_be_visible()
            invite = page.locator("span.font-mono").first.inner_text(timeout=10000).strip()
            assert "/interview/" in invite, "INVITE-02: no invite URL in browser"
            token = invite.rsplit("/", 1)[-1]

            # An actual HTTP read proves that the invite was persisted and belongs to a session.
            auth = page.evaluate("localStorage.getItem('auth_token')")
            assert auth
            sessions = page.request.get(
                f"{API_BASE}/assessments/{data['assessment_id']}/sessions",
                headers={"Authorization": f"Bearer {auth}"},
            )
            assert sessions.ok, f"session list failed: {sessions.status}"
            rows = sessions.json()["data"]["sessions"]
            created = next(s for s in rows if s["candidate_name"] == "Synthetic Browser Guest")
            sid = created["id"]
            assert created["invite_url"].endswith(token)

            candidate = context.new_page()
            candidate.goto(invite, wait_until="domcontentloaded")
            expect(candidate.get_by_role("heading", name="E2E Browser Assessment")).to_be_visible(timeout=15000)
            print("BROWSER-DB-01 / INVITE-02: real browser login, invitation UI and persisted HTTP read PASS")

            # Real WebSocket handshake: bad token fails, member token gets tenant-owned state.
            coverage_url = f"ws://127.0.0.1:3001/ws/sessions/{sid}/coverage"
            bad = ws_message(page, coverage_url, {"type": "auth", "token": "invalid.test.token"})
            assert bad["opened"] and any(m["code"] == "auth_failed" for m in bad["messages"]), bad
            allowed = ws_message(page, coverage_url, {"type": "auth", "token": auth})
            assert allowed["opened"] and any(m["type"] == "coverage_update" for m in allowed["messages"]), allowed
            print("WS-AUTH-05: real WebSocket upgrade denied foreign token and delivered owner coverage PASS")

            # Revoke in the authenticated UI session through HTTP; ensure the browser link
            # and AUDIO WebSocket reject the old token without contacting Gemini.
            revoked = page.request.post(
                f"{API_BASE}/sessions/{sid}/revoke_invite",
                headers={"Authorization": f"Bearer {auth}"},
            )
            assert revoked.ok, f"revoke failed with {revoked.status}"
            old_link = page.request.get(f"{API_BASE}/sessions/{quote(token)}/candidate")
            assert old_link.status == 404
            audio = ws_message(
                page,
                f"ws://127.0.0.1:3001/ws/sessions/{sid}/audio?token={quote(token)}",
                {"type": "ping"},
            )
            assert audio["opened"] and any(m["code"] == "auth_failed" for m in audio["messages"]), audio
            print("INVITE-04: revoked invite fails both HTTP and actual audio WS handshake PASS")
        except Exception:
            page.screenshot(path="browser-e2e-failure.png", full_page=True)
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
