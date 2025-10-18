# Neuro-OS
Neuro OS is an forwarding method that allows Neuro & Evilyn to use the windows operatng system.
> [!DANGER]
> Use at your own risk.
> Neuro-OS directly interfaces with the Windows system layer and executes actions based on Neuro’s or Evilyn’s runtime behavior.
> This means your files, settings, and applications can and will be affected depending on their mood or state during use.
> <br><br>We strongly recommend running this in a sandboxed environment or virtual machine.
> <br>DO NOT install or run Neuro-OS on your main computer.

## Installation
To install this application, you will have to download and setup the repository (An .exe package is coming soon).
<br><br>Then install the python packages from ``requirements.txt``, and then Neuro-OS requires version ``0.0.1-alpha`` of the windows-api.
<br><br>As all Neuro-OS does is port the websocket functions from windows-api's interaction-api to the Neuro-sdk.
<br><br>You can download it here: [``https://github.com/Nakashireyumi/windows-api/tree/0.0.1-alpha``](https://github.com/Nakashireyumi/windows-api/tree/0.0.1-alpha)
<br>Then you'll have to extract the source folder, and place them in the root repository path. So here:
```
root/
├── .venv/ # Virtual environment
├── .vscode/ # VSCode workspace settings
├── neuro-sdk/ # SDK package or module
├── screenshots/ # Screenshots for documentation
├── src/ # Source code
│ ├── dev/
│ │ ├── interaction-client/ # WebSocket/interaction layer
│ │ │ ├── main.py
│ │ │ ├── client.py
│ │ │ └── pycache/
│ │ └── utils/ # Shared utility scripts
│ │ ├── loadConfig.py
│ │ ├── winapi_management.py
│ │ ├── launch.py
│ │ └── pycache/
│ ├── global/ # Global definitions/configs
│ ├── implementations/ # Core feature implementations
│ └── resources/ # Static or runtime resources
|
├── windows-api/ # Windows interaction backend <-- Place it like this, here
|
├── .gitignore
├── README.md
└── requirements.txt