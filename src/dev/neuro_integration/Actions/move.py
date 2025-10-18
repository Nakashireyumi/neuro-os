from neuro_api.command import Action

def schema():
    return Action(
        "move",
        "Move the mouse",
        {
            "type": "object",
            "properties": {
                "coordinates": {
                    "type": "object",
                    "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}
                },
            },
            "required": ["coordinates"]
        }
    )
