# Neuro-OS
Neuro OS is an forwarding method that allows Neuro & Evilyn to use the windows operatng system.
> [!CAUTION]
> This software allows neuro / evilyn to interface with your windows machine thru direct user inputs (i.e. mouse, keyboard, etc).
> <br>You can very easily lose control, depending on neuro's / evilyn's mood during usage. We highly recommend a virtual machine.<br><br>
> Use at your own risk.

## Installation
To install this application, you will have to download and setup the repository (An .exe package is coming soon).
<br><br>Then install the python packages from ``requirements.txt``, and then Neuro-OS requires version ``0.0.1-alpha`` of the windows-api.
<br><br>As all Neuro-OS does is port the websocket functions from windows-api's interaction-api to the Neuro-sdk.

### Deprrcation warning
This is no longet needed, as neuro-os now have a gitmodule for that now.
Thanks [KTrain5169](https://github.com/KTrain5169)
(P.S. I didn't know a git module existed - Nakurity)

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
