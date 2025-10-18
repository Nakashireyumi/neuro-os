# Neuro-OS

Neuro OS is an forwarding method that allows Neuro & Evilyn to use the windows operatng system.
> [!CAUTION]
> This software allows neuro / evilyn to interface with your windows machine thru direct user inputs (i.e. mouse, keyboard, etc).
>
> You can very easily lose control, depending on neuro's / evilyn's mood during usage. We highly recommend a virtual machine.
>
>
> Use at your own risk.

## Installation

> [!NOTE]
> Thanks [KTrain5169](https://github.com/KTrain5169) for adding the submodule and somewhat rewriting this section.
>
> (P.S. I didn't know a git module existed - Nakurity)

To install this application, you will have to download and setup this repository.
EXE coming soon:tm:.

If you are cloning via `git`, the `git clone` command has a `--recursive-submodules` flag that automatically checks out the `windows-api` submodule.
Otherwise, you will need to manually run `git submodule update --init`.

Afterwards, you need to install packages for both the `neuro-os` repository and the `windows-api` submodule.
Both `neuro-os` and `windows-api` requires `pip`, but `windows-api` also requires `vcpkg` to build the C++ components.
Refer to [`windows-api`s README file](./windows-api/README.md) for complete install instructions.

This should be your repository structure now:

```ruby
root/
├── .venv/ # Virtual environment
├── src/ # Source code
│ ├── dev/
│ │ ├── interaction-client/ # WebSocket/interaction layer
│ │ │ ├── __main__.py
│ │ │ └── client.py
│ │ └── utils/ # Shared utility scripts
│ │   ├── loadConfig.py
│ └── launch.py
|
├── windows-api/ # Windows interaction backend
|
├── .gitignore
├── .gitmodules
├── LICENSE
├── README.md
└── requirements.txt
```

## Starting the client
```cmd
(.venv) PS A:\neuro-os> python -m src.dev.interaction-client
```
This assumes you are in an virtual python environment by now. And the command above starts the client
