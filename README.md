# Neuro Desktop
Neuro-OS allows Neuro and Evil Neuro to interact with Windows through direct control of mouse, keyboard, and UI elements. The system now features **OCR-based UI detection** and optional **AI vision analysis** for intelligent interaction.

**v0.0.2-alpha** - Enhanced UI context detection for Neuro & Evil Neuro's Windows integration.

> [!CAUTION]
> This software allows Neuro/Evil to control your Windows machine directly (mouse, keyboard, clicks).
> You (vedal) may lose control of your system temporarily, depending on their mood.
> **We highly recommend (vedal) using a virtual machine for usage with Neuro and Evil.**

**For Development**: This caution mainly applies when connected to the live Neuro backend. During development, Neuro-OS simply executes the most recent action from the API. A safety monitor and user priority system are planned for future releases.

## ✨ What's New in v0.0.2-alpha

- **OCR-based UI detection**: Automatically detects text, buttons, links with exact coordinates
- **Vision API integration**: Optional AI-powered screenshot analysis
- **Session-based security**: Secure authentication for backend APIs
- **Enhanced context**: Neuro sees detailed UI elements instead of just windows
- **Fixed bugs**: Coordinate validation, context message formatting

## 📦 Installation

### Prerequisites
- Python 3.8+ with `pip` / `uv`
- Git (with submodules support)
- Windows 10/11

### Quick Start

```bash
# 1. Clone repository with submodules
git clone --recursive https://github.com/Nakashireyumi/neuro-desktop.git
cd neuro-desktop

# 2. Initialize submodules (if not cloned with --recursive)
git submodule update --init --recursive

# 3. Setup an virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 4. Install neuro-os Python dependencies
pip install -r requirements.txt

# 5. Setup windows-api submodule
cd windows-api

# Install dependencies
pip install -r requirements.txt
cd ..

# 6. Run neuro-desktop
python -m neuro-desktop
```

## 🚀 Usage

### Start Neuro Desktop

```bash
python -m neuro-desktop
```

This starts:
- Windows interaction server (port 8766)
- Neuro Desktop Integration

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

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)**: Version history and updates
- **[QUICKSTART.md](QUICKSTART.md)**: Quick setup guide
- **[windows-api/README.md](windows-api/README.md)**: Windows API setup

## 🐛 Known Issues

### Windows-API Port Hangs
- **Issue**: Port 8766 remains occupied after stopping
- **Workaround**: Manually kill process or restart
- **Status**: Fix planned

### Jippity not knowing what to do with neuro desktop
- **Issue**: No actual contextual goal for using this integration (this would apply to neuro/evilyn as well)
- **Workaround**: Tell jippity what to do.
- **Possible fixes**:
    - Tell neuro/evil what to do
    - Add an long term memory integration, that bundles with neuro desktop. To ensure neuro and evil's long term memory. Possibly with a worse or better implementation, who knows!
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
Tools you may need, or want during developmemnt of a contribution

- **Unofficial Windows API (by nakurity)**: https://github.com/nakurity/windows-api
- **Neuro SDK**: https://github.com/VedalAI/neuro-sdk
- **Gary**: https://github.com/Govorunb/gary

---

**Version**: 0.0.3-devbuild  
**Last Updated**: 2025-11-04
**Status**: 🚧 Alpha - Active Development
