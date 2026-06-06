import json

from pointiv_extension_sdk import Input, output
from pointiv_extension_sdk import google_calendar, google_gmail, http, log, storage


def execute(input_json: str) -> str:
    data = json.loads(input_json)
    inp = Input(
        text=data.get("text", ""),
        context=data.get("context", ""),
        command=data.get("command", ""),
    )
    result = _run(inp)
    return json.dumps({"type": result.type, "value": result.value})


def _run(inp: Input):
    cmd = inp.command.strip().lower()

    if cmd == "http":
        return _demo_http()
    if cmd in {"calendar", "cal"}:
        return _demo_calendar(inp)
    if cmd.startswith("gmail") or cmd == "email":
        return _demo_gmail(inp)

    count = int(storage.read("run_count") or "0") + 1
    storage.write("run_count", str(count))

    log.info(
        f"execute: count={count}, text_len={len(inp.text)}, cmd={inp.command!r}",
    )

    name = inp.text.strip()
    greeting = "Hello, World!" if not name else f"Hello, {name}!"

    return output.text(
        f"{greeting}\n\nRun #{count}. Commands: http, calendar, gmail to@example.com",
    )


def _demo_http():
    resp = http.get("https://httpbin.org/get")
    if resp.status == 403:
        return output.error(
            'network permission not granted. Add "network" to pointiv-extension.json.',
        )
    if resp.status == 0:
        return output.error("HTTP request failed (host returned no response).")
    preview = resp.body[:400]
    return output.text(f"HTTP {resp.status}\n\n{preview}")


def _demo_calendar(inp: Input):
    text = inp.text.strip()
    title = "Pointiv test event"
    date = "2026-12-01"

    if len(text) == 10 and text[4] == "-":
        date = text
    elif text:
        title = text

    try:
        result = google_calendar.schedule(
            title,
            date,
            "15:00",
            "15:30",
            "Created by the Hello World example extension",
        )
        return output.text(f"Calendar event created.\n\n{json.dumps(result)}")
    except RuntimeError as error:
        return output.error(f"Calendar failed: {error}")


def _demo_gmail(inp: Input):
    parts = inp.command.split()
    to = parts[1].strip() if len(parts) > 1 else ""
    if not to or "@" not in to:
        return output.error(
            "Usage: gmail you@example.com\n"
            "Put the email address in the command. Optional body in selected text.",
        )

    body = inp.text.strip() or "Sent from the Pointiv Hello World example extension."

    try:
        result = google_gmail.send(to, "Hello from Pointiv", body)
        return output.text(f"Email sent to {to}.\n\n{json.dumps(result)}")
    except RuntimeError as error:
        return output.error(f"Gmail failed: {error}")
