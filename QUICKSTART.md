# Quick Start Guide - Enhanced Neuro-OS

## 🚀 What's New

Your neuro-os system now has **massively improved UI context detection**! Neuro can now:

1. ✅ **See all text on screen** with exact coordinates (via OCR)
2. ✅ **Detect buttons, links, and inputs** automatically
3. ✅ **Get AI-powered UI analysis** (optional, via Groq Vision API)
4. ✅ **Secure session-based authentication** (no more shared API keys)
5. ✅ **Fixed malformed context messages**

---

## 📦 Installation

### Prerequisites
- Python 3.8+ with `pip`
- Node.js (for automated setup)
- [vcpkg](https://vcpkg.io/) (for windows-api C++ components)
- Git with submodule support

### Option 1: Automated Setup (Recommended)

```bash
# Clone with submodules
git clone --recursive https://github.com/Nakashireyumi/neuro-os.git
cd neuro-os

# Run automated setup
node src/bin/neuro-setup.js --run
```

This installs:
- Python dependencies (requirements.txt)
- OCR libraries (easyocr, opencv-python, pillow)
- Vision API client (requests)
- windows-api submodule dependencies

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone --recursive https://github.com/Nakashireyumi/neuro-os.git
cd neuro-os

# 2. Install neuro-os dependencies
pip install -r requirements.txt

# 3. Install OCR dependencies
pip install easyocr opencv-python pillow numpy requests

# 4. Setup windows-api submodule
cd windows-api
vcpkg install
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r src/contributions/cassitly/python/requirements.txt
cd ..

# 5. Run neuro-os
python -m src.dev.launch
```

### Optional: Enable Vision API

For AI-powered screenshot analysis:

```python
# In src/dev/neuro_integration/client.py, line 34
self._reg = RegionalizationCore(enable_vision_api=True)
```
```

---

## 🎮 Usage

### Start Neuro-OS Normally

```bash
cd neuro-os
python -m src.dev.launch
```

That's it! OCR will run automatically every 2 seconds.

### What Neuro Sees Now

**Before** (only windows):
```
Available Actions (15):
  - click_window_67420: Click on Visual Studio Code
  - click_window_198602: Click on Terminal
```

**After** (rich UI context):
```
Screen Resolution: 1920x1080 (coordinates: 0-1919, 0-1079)
Mouse Position: (640, 480)
Text near mouse: "Subscribe"

Detected Text on Screen (127 items):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Share" at (520, 450)
  - "Comments" at (640, 700)
  ... and 123 more text items

UI Elements Detected: 45 total

Buttons (12):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Play" at (960, 540)

Links (8):
  - "Evil Neuro's Channel" at (200, 150)
  - "Watch Later" at (1700, 300)

Visible Text (25 items):
  - "Evil Neuro Glitches After Update" at (400, 100)
  - "12M views" at (400, 130)
```

---

## 🎯 How It Works

### OCR Detection (Always Active)
- Runs **every 2 seconds**
- Detects **text, buttons, links, inputs**
- Provides **exact coordinates** for clicking
- **Zero API calls** (runs locally)

### Vision API (Optional)
- Runs **every 20 seconds** (less frequent)
- Uses **Groq Llama Vision** for semantic understanding
- Provides **contextual descriptions** of UI
- Requires **Nakurity backend** with Groq API key

---

## 🔧 Configuration

### Enable/Disable Vision API

```python
# In src/dev/neuro_integration/client.py
self._reg = RegionalizationCore(enable_vision_api=True)   # Enable
self._reg = RegionalizationCore(enable_vision_api=False)  # Disable (default)
```

### Change OCR Update Frequency

```python
# In src/regionalization/core.py, line 421
self.update_interval = 2.0  # seconds (change to 1.0 for faster updates)
```

### Change Vision API Frequency

```python
# In src/regionalization/core.py, line 426
self._vision_update_interval = 10  # Update every 10 cycles (20 seconds)
# Change to 5 for faster vision updates (every 10 seconds)
```

---

## 🧪 Testing

### Test OCR Detection

```python
from src.regionalization.ocr_detector import OCRDetector

detector = OCRDetector()
elements = detector.detect_elements()

for elem in elements[:10]:
    print(f"{elem.element_type}: '{elem.text}' at ({elem.center_x}, {elem.center_y})")
```

### Test Vision API

```python
from src.regionalization.vision_api_client import VisionAPIClient

client = VisionAPIClient()
analysis = client.analyze_screenshot()
print(analysis)
```

---

## 🐛 Troubleshooting

### "OCR not available"
**Solution**: Install EasyOCR or Tesseract
```bash
pip install easyocr opencv-python
```

### "Vision API authentication failed"
**Solution**: Vision API is optional. Either:
- Disable it: `enable_vision_api=False`
- Or configure Nakurity backend with Groq API key

### "Context messages duplicated"
**Solution**: Already fixed! String concatenation issue resolved in `client.py`

### OCR too slow
**Solution**: Reduce update frequency
```python
self.update_interval = 5.0  # Update every 5 seconds instead of 2
```

---

## 📊 Performance Tips

### For Best OCR Performance
- Use **1920x1080 resolution** (standard)
- Ensure **good text contrast** (dark text on light background)
- Avoid **very small fonts** (<10pt)

### For Best Vision API Performance
- Keep **update interval high** (20+ seconds)
- Use for **complex UIs** where OCR isn't enough
- Disable if not needed to save API costs

---

## 🎉 Example: Neuro Clicking YouTube Subscribe

**Old system** (coordinates only):
```
Neuro: I'll click the subscribe button
Action: click(x=640, y=480)  # Had to guess or be told coordinates
```

**New system** (intelligent):
```
Neuro sees:
  - "Subscribe" button at (640, 480)
  - "Like" button at (320, 450)
  - Video title "Evil Neuro Glitches"

Neuro: I'll click the Subscribe button at 640, 480
Action: click(x=640, y=480)  # Knows exactly what it's clicking!
```

---

## 📝 What Changed

### Files Modified
- ✅ `nakurity-backend/api/session-store.js` - New shared session module
- ✅ `nakurity-backend/api/session.js` - Now uses shared store
- ✅ `nakurity-backend/api/vision.js` - Already uses shared validation
- ✅ `neuro-os/src/dev/neuro_integration/client.py` - Fixed context formatting
- ✅ `neuro-os/src/regionalization/vision_api_client.py` - Session-based auth
- ✅ `neuro-os/src/regionalization/core.py` - Vision API integration

### New Features
- ✅ OCR-based UI element detection (already existed, now integrated)
- ✅ Vision API integration (optional)
- ✅ Session-based authentication
- ✅ Clean context messages
- ✅ Automatic session management

---

## 🚀 Next Steps

1. **Test the system**: Run neuro-os and see the rich context in logs
2. **Enable vision API**: If you want AI analysis, set `enable_vision_api=True`
3. **Deploy backend**: Push nakurity-backend changes to Vercel
4. **Monitor logs**: Watch `[CONTEXT]` logs to see what Neuro sees

---

**Need Help?** Check `IMPROVEMENTS.md` for detailed documentation.

**Status**: ✅ Ready to use!
