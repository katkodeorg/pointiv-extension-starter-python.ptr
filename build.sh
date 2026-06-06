#!/usr/bin/env bash
set -euo pipefail

OUTPUT="extension.wasm"

if [[ "${1:-}" == "--check" ]]; then
  command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
  echo "Toolchain OK (python3 found)"
  exit 0
fi

if ! command -v componentize-py >/dev/null; then
  echo "componentize-py not found."
  echo "Install with: pip install componentize-py"
  exit 1
fi

python3 -m pip install -e ../pointiv-extension-sdk-python 2>/dev/null || \
  python3 -m pip install pointiv-extension-sdk

componentize-py -d src -w "$OUTPUT" componentize main execute

echo ""
echo "Built $OUTPUT"
echo "Next steps:"
echo "  git add $OUTPUT"
echo "  git commit -m 'build: update extension.wasm'"
echo "  git push"
