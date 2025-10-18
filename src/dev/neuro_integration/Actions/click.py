from neuro_api.command import Action

def schema():
    return Action(
        "click",
        "If coordinates for the mouse is provided, move the mouse to that area, then click",
        {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "enum": ["left", "right", "middle"]}
            },
            "required": ["button"]
        }
    )
