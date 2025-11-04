## How to run tests

```cmd
# From repo root on your machine
python -m pip install --user -U pytest flask pyyaml

# Ensure Python can import "src.*" by including the neuro-desktop folder on PYTHONPATH
export PYTHONPATH="$PWD/neuro-desktop${PYTHONPATH:+:$PYTHONPATH}"

# Run tests (they will skip gracefully if endpoints/modules are not present in your checkout)
python -m pytest -q
```