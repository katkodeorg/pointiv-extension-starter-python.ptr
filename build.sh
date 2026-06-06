#!/usr/bin/env bash
set -euo pipefail

OUTPUT="extension.wasm"
EXTISM_PY="${EXTISM_PY:-extism-py}"

resolve_extism_py() {
  if [[ -x "$EXTISM_PY" ]]; then
    return 0
  fi
  if command -v "$EXTISM_PY" >/dev/null; then
    EXTISM_PY="$(command -v "$EXTISM_PY")"
    return 0
  fi
  for candidate in \
    "$HOME/.local/bin/extism-py" \
    /usr/local/bin/extism-py; do
    if [[ -x "$candidate" ]]; then
      EXTISM_PY="$candidate"
      return 0
    fi
  done
  return 1
}

install_sdk() {
  if [[ -n "${POINTIV_SDK_PATH:-}" ]]; then
    python -m pip install -e "$POINTIV_SDK_PATH" --quiet
    return
  fi
  for candidate in \
    ../pointiv-extension-sdk-python \
    ./pointiv-extension-sdk-python; do
    if [[ -f "$candidate/pyproject.toml" ]]; then
      python -m pip install -e "$candidate" --quiet
      return
    fi
  done
  python -m pip install "pointiv-extension-sdk>=0.3.4" --quiet
}

if [[ "${1:-}" == "--check" ]]; then
  command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
  resolve_extism_py || {
    echo "extism-py not found."
    echo "Run with: EXTISM_PY=\"\$HOME/.local/bin/extism-py\" ./build.sh --check"
    exit 1
  }
  command -v wasm-opt >/dev/null || { echo "wasm-opt not found (brew install binaryen)"; exit 1; }
  echo "Toolchain OK ($EXTISM_PY)"
  exit 0
fi

if ! resolve_extism_py; then
  echo "extism-py not found."
  echo "Install from: https://github.com/extism/python-pdk/releases"
  echo "Then run:"
  echo "  EXTISM_PY=\"\$HOME/.local/bin/extism-py\" ./build.sh"
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip --quiet
install_sdk

SDK_ROOT="$(python -c 'import pointiv_extension_sdk, pathlib; print(pathlib.Path(pointiv_extension_sdk.__file__).resolve().parent.parent)')"
export PYTHONPATH="${SDK_ROOT}${PYTHONPATH:+:$PYTHONPATH}"

BUILD_ENTRY=".build/entry.py"
mkdir -p .build
cat src/host_bindings.py src/main.py > "$BUILD_ENTRY"
"$EXTISM_PY" "$BUILD_ENTRY" -o "$OUTPUT"

SIZE_KB=$(( $(wc -c < "$OUTPUT") / 1024 ))
SHA=$(shasum -a 256 "$OUTPUT" | awk '{print $1}')

echo ""
echo "Built $OUTPUT (${SIZE_KB} KB)"
echo "SHA-256: $SHA"
echo ""
echo "Next steps:"
echo "  git add $OUTPUT"
echo "  git commit -m 'build: update extension.wasm'"
echo "  git push"
