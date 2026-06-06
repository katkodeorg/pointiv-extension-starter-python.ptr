# Hello World Pointiv Extension

Minimal Python/WASM starter for Pointiv. Greets by name with no SDK or host API calls.

Use this to verify the Python/extism-py toolchain and Pointiv runtime before adding `pointiv-extension-sdk` features like storage, HTTP, or Google.

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

`build.sh` uses `EXTISM_PY` so you don't need to add `~/.local/bin` to your global PATH.

## Fork

Your GitHub repo URL is your extension's identity.

1. Edit `pointiv-extension.json` (`name`, `author`)
2. Edit `src/main.py`
3. `./build.sh`, commit `extension.wasm`, push

After the minimal starter works in Pointiv, add SDK features incrementally:

1. `storage` for run counter
2. `log`
3. `http`, `google_calendar`, `google_gmail`

SDK: [pointiv-extension-sdk](https://pypi.org/project/pointiv-extension-sdk)
