import json

import extism


@extism.plugin_fn
def execute():
    data = json.loads(extism.input_str())
    name = data.get("text", "").strip()
    greeting = "Hello, World!" if not name else f"Hello, {name}!"
    extism.output_str(json.dumps({"type": "text", "value": greeting}))
