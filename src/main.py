import json

import extism

from pointiv_extension_sdk import Input, output
from pointiv_extension_sdk import google_calendar, google_gmail, http, log, storage, tile


@extism.plugin_fn
def execute():
    data = json.loads(extism.input_str())
    inp = Input(
        text=data.get("text", ""),
        context=data.get("context", ""),
        command=data.get("command", ""),
    )
    result = _run(inp)
    extism.output_str(json.dumps({"type": result.type, "value": result.value}))


def _run(inp: Input):
    cmd = inp.command.strip().lower()

    if cmd == "todo" or cmd.startswith("todo "):
        # Tile actions land here too: clicking "Done" on a tile row runs
        # `todo done <n>` through this same execute function.
        return _todo_command(inp.command.strip())
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
        f"{greeting}\n\nRun #{count}. Commands: todo add <text>, http, calendar, gmail to@example.com",
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

# -- Todo list + tile ---------------------------------------------------------
#
# The todo list demonstrates the tile feature end to end: `execute` mutates
# the list in extension storage, `render_tile` reads the same storage and
# returns a declarative tile dict for the host to draw.


def _load_todos():
    raw = storage.read("todos")
    if raw is None:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def _save_todos(todos):
    storage.write("todos", json.dumps(todos))


def _todo_command(command: str):
    """Handle `todo add <text>`, `todo done <n>`, `todo list`."""
    rest = command[len("todo"):].strip()
    verb, _, arg = rest.partition(" ")
    arg = arg.strip()

    if verb == "add" and arg:
        todos = _load_todos()
        # Cap stored text so tile rows stay well under the host's 300-char
        # row limit.
        text = arg[:280]
        todos.append({"text": text, "done": False})
        _save_todos(todos)
        return output.text(f"Added todo #{len(todos)}: {text}")

    if verb == "done":
        # Indices are 1-based positions in the stored array, the same
        # numbering `todo list` prints and the tile rows use.
        todos = _load_todos()
        try:
            n = int(arg)
        except ValueError:
            n = 0
        if n < 1 or n > len(todos):
            if not todos:
                return output.error("No todos yet. Add one with: todo add <text>")
            return output.error(f"Usage: todo done <n> (1..{len(todos)})")
        todos[n - 1]["done"] = True
        _save_todos(todos)
        return output.text(f"Done: {todos[n - 1]['text']}")

    if verb in {"list", ""}:
        todos = _load_todos()
        if not todos:
            return output.text("No todos yet. Add one with: todo add <text>")
        lines = [
            f"{i + 1} {'[x]' if t['done'] else '[ ]'} {t['text']}"
            for i, t in enumerate(todos)
        ]
        return output.text("\n".join(lines))

    return output.error("Usage: todo add <text> | todo done <n> | todo list")


@extism.plugin_fn
def render_tile():
    """Render the "Todos" tile.

    The host calls this when the popup opens and again after a tile action
    runs. Only storage host calls are available here, and the render has a
    3 second budget. Input is {"now": "<RFC3339>"} when you need the time:
    json.loads(extism.input_str()).
    """
    todos = _load_todos()
    open_count = sum(1 for t in todos if not t["done"])

    # Badge first: open count in warn, or an ok "all done" badge.
    if open_count > 0:
        body = [tile.badge(f"{open_count} open", tone="warn")]
    else:
        body = [tile.badge("all done", tone="ok")]

    # Up to 5 not-done rows. Each row's action command carries the item's
    # 1-based index in the stored array, so `todo done <n>` hits the right
    # item even when done items sit between open ones.
    shown = 0
    for i, t in enumerate(todos):
        if t["done"] or shown >= 5:
            continue
        # The host rejects the whole tile if any row text exceeds 300 chars,
        # so truncate defensively (older stored todos may predate the add cap).
        text = t["text"] if len(t["text"]) <= 280 else t["text"][:280] + "…"
        body.append(
            tile.row(text, actions=[tile.action("Done", f"todo done {i + 1}")]),
        )
        shown += 1

    ui = tile.tile(
        "Todos",
        body=body,
        footer=[tile.action("Refresh", "todo list")],
    )
    tile.output_tile(ui)
