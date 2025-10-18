from neuro_api.command import Action

class Click:
    def schema():
       Action(
         name="click",
         description="If coordinates is provided, move the mouse to that area, then click",
         schema={
           "type": "object",
           "properties": {
               "coordinates": {"type": "integer", "x": 0, "y": 0},
               "button": {"type": "string", "button": "left"}
           },
          "required": ["button"]
         }
      )
