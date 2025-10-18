# todo: make this export and initialoze the action schema for the neuro-client
import os
import importlib

from neuro_api.command import check_action


def load_actions(game_name):
  # Load all Action definitions dynamically
  actions = []
  for file in os.listdir(ACTIONS_DIR):
      if not file.endswith(".py") or file.startswith("__"):
          continue

      file_path = os.path.join(ACTIONS_DIR, file)
      spec = importlib.util.spec_from_file_location(file[:-3], file_path)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)

      if hasattr(module, "schema"):
          act = module.schema()
          check_action(act)
          actions.append(act)
          print(f"[ACTION] Loaded: {act.name}")

return actions
