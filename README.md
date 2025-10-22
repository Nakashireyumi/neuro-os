# Neuro-OS

**v0.0.2-alpha** - Enhanced UI context detection for Neuro & Evil Neuro's Windows integration.

Neuro-OS allows Neuro and Evil Neuro to interact with Windows through direct control of mouse, keyboard, and UI elements. The system now features **OCR-based UI detection** and optional **AI vision analysis** for intelligent interaction.

> [!CAUTION]
> This software allows Neuro/Evil to control your Windows machine directly (mouse, keyboard, clicks).
> You may lose control of your system temporarily, depending on their mood.
> **We highly recommend using a virtual machine for testing.**
>
> Use at your own risk.

**For Development**: This caution mainly applies when connected to the live Neuro backend. During development, Neuro-OS simply executes the most recent action from the API. A safety monitor and user priority system are planned for future releases.

## ✨ What's New in v0.0.2-alpha

- **OCR-based UI detection**: Automatically detects text, buttons, links with exact coordinates
- **Vision API integration**: Optional AI-powered screenshot analysis
- **Session-based security**: Secure authentication for backend APIs
- **Enhanced context**: Neuro sees detailed UI elements instead of just windows
- **Fixed bugs**: Coordinate validation, context message formatting

## 📦 Installation

### Prerequisites
- Python 3.8+ with `pip`
- Git (with submodules support)
- Windows 10/11

### Quick Start

```bash
# 1. Clone repository with submodules
git clone --recursive https://github.com/Nakashireyumi/neuro-os.git
cd neuro-os

# 2. Initialize submodules (if not cloned with --recursive)
git submodule update --init --recursive

# 3. Install neuro-os Python dependencies
pip install -r requirements.txt

# 4. Install OCR dependencies (for UI detection)
pip install easyocr opencv-python pillow numpy requests

# 5. Setup windows-api submodule
cd windows-api
# Install vcpkg dependencies (requires vcpkg)
vcpkg install
# Setup Python venv and install dependencies
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r src/contributions/cassitly/python/requirements.txt
cd ..

# 6. Run neuro-os
python -m src.dev.launch
```

### Automated Setup (Recommended)

Use the setup script to install everything:

```bash
# Install and run
node src/bin/neuro-setup.js --run

# Or just install dependencies
node src/bin/neuro-setup.js
```

### Optional: Enable Vision API

For AI-powered screenshot analysis:

```python
# In src/dev/neuro_integration/client.py, line 34
self._reg = RegionalizationCore(enable_vision_api=True)
```

## 🚀 Usage

### Start Neuro-OS

```bash
python -m src.dev.launch
```

This starts:
- Windows interaction server (port 8766)
- Neuro API integration (port 8000)
- Regionalization system with OCR

### What Neuro Can See

With v0.0.2-alpha, Neuro receives detailed UI context:

```
Screen Resolution: 1920x1080
Mouse Position: (640, 480)
Active Application: chrome.exe

Detected Text on Screen (127 items):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Share" at (520, 450)
  ... and 124 more items

UI Elements Detected: 45 total

Buttons (12):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Play" at (960, 540)

Visible Windows:
  1. Evil Neuro - YouTube [FOCUSED]
     Position: (0, 0), Size: 1920x1080
```

## 📁 Repository Structure

```
neuro-os/
├── src/
│   ├── regionalization/       # UI detection system
│   │   ├── core.py           # Main regionalization
│   │   ├── ocr_detector.py   # OCR-based detection
│   │   └── vision_api_client.py # AI vision client
│   ├── dev/
│   │   ├── neuro_integration/ # Neuro API integration
│   │   └── utils/            # Utilities
│   └── types/
│       └── neuro_types.py    # Type definitions
├── windows-api/              # Windows control (submodule)
├── CHANGELOG.md              # Version history
├── QUICKSTART.md             # Quick start guide
└── README.md                 # This file
```

## 🔧 Configuration

### OCR Update Frequency
```python
# In src/regionalization/core.py, line 421
self.update_interval = 2.0  # seconds (default: 2s)
```

### Vision API Frequency
```python
# In src/regionalization/core.py, line 426
self._vision_update_interval = 10  # cycles (default: 20s)
```

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)**: Version history and updates
- **[QUICKSTART.md](QUICKSTART.md)**: Quick setup guide
- **[windows-api/README.md](windows-api/README.md)**: Windows API setup

## 🐛 Known Issues

### Windows-API Port Hangs
- **Issue**: Port 8766 remains occupied after stopping
- **Workaround**: Manually kill process or restart
- **Status**: Fix planned

### OCR Limitations
- Requires EasyOCR or Tesseract installation
- May miss very small or low-contrast text
- Works best with standard fonts

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🔗 Links

- **Nakurity Backend**: https://github.com/Nakashireyumi/nakurity-backend
- **Windows API**: https://github.com/Nakashireyumi/windows-api
- **Neuro-sama**: https://www.twitch.tv/vedal987

---

**Version**: 0.0.2-alpha  
**Last Updated**: 2025-01-22  
**Status**: 🚧 Alpha - Active Development
