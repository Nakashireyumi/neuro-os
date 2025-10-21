from neuro_api.command import Action

def schema():
    return Action(
        "dragto",
        "Drag from current mouse position to specified coordinates",
        {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "duration": {
                    "type": "number", 
                    "minimum": 0
                },
                "button": {
                    "type": "string", 
                    "enum": ["left", "right", "middle"]
                }
            },
            "required": ["x", "y"]
        }
    )