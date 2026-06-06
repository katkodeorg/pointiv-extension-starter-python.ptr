# Hello World Pointiv Extension

Python/WASM template for Pointiv. Greets by name, keeps a run counter, and includes small demos for HTTP, Calendar, and Gmail.

## Install

Paste your GitHub URL in Pointiv Extensions:

```
https://github.com/<your-username>/<your-repo>
```

## Build

Needs [`extism-py`](https://github.com/extism/python-pdk) and [Binaryen](https://github.com/WebAssembly/binaryen) (`brew install binaryen`). `./build.sh` writes `extension.wasm` to the repo root. Commit that file so Pointiv can load it from GitHub.

```sh
brew install binaryen
curl -Ls https://raw.githubusercontent.com/extism/python-pdk/main/install.sh | bash
EXTISM_PY="$HOME/.local/bin/extism-py" ./build.sh
```

`build.sh` uses `EXTISM_PY` so you don't need to add `~/.local/bin` to your global PATH. It installs `pointiv-extension-sdk` from a sibling checkout, `POINTIV_SDK_PATH`, or PyPI, then merges `src/host_bindings.py` + `src/main.py` into a single entry file for extism-py.

## Try the API demos

Add the permissions you need in `pointiv-extension.json`, rebuild, reinstall.

| Command | Permission | What happens |
|---------|------------|--------------|
| `http` | `network` | GET https://httpbin.org/get, show status and body |
| `calendar` or `cal` | `google_calendar` | Create a test event (title from selection; optional date `YYYY-MM-DD`) |
| `gmail you@example.com` | `google_gmail` | Send mail (body from selection) |

Google commands need Google connected in Pointiv Settings > Account.

Default behavior (any other command): hello + run counter.

## Fork

Your GitHub repo URL is your extension's identity.

1. Edit `pointiv-extension.json` (`name`, `author`, `permissions`)
2. Edit `src/main.py` and `src/host_bindings.py` (add host imports for any new SDK modules)
3. `./build.sh`, commit `extension.wasm`, push

SDK: [pointiv-extension-sdk](https://pypi.org/project/pointiv-extension-sdk)

## Permissions

| Permission | Grants |
|------------|--------|
| `storage` | Key/value store |
| `clipboard_read` | Clipboard |
| `network` | `http.get`, `http.post`, `http.request` |
| `google_calendar` | `google_calendar.schedule` |
| `google_gmail` | `google_gmail.send` |

Calls without permission fail safely (empty data or an error message).
