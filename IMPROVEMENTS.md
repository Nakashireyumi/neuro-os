# Neuro-OS & Nakurity Backend Improvements

## Summary

This document outlines the comprehensive improvements made to **neuro-os** and **nakurity-backend** to enable rich UI context detection, secure API access, and AI-powered vision analysis for Neuro's Windows integration.

---

## 🎯 Goals Achieved

### 1. **Fixed Context Message Formatting**
- **Problem**: Context messages showed malformed action descriptions like `clickNeuro-OS Windows integration is active...`
- **Solution**: Fixed string concatenation in `neuro_integration/client.py` to properly format action registration messages
- **Impact**: Neuro now receives clean, readable context messages

### 2. **Session-Based Authentication System**
- **Problem**: Static API keys are insecure and can be shared/stolen
- **Solution**: Implemented dynamic session management with:
  - Session claim/heartbeat/release endpoints
  - Machine fingerprinting (IP + User-Agent hash)
  - Automatic expiration (5-minute timeout)
  - Heartbeat keep-alive mechanism
- **Location**: `nakurity-backend/api/session-store.js` (shared module)
- **Impact**: Secure, per-instance authentication that auto-terminates

### 3. **Vision API Integration**
- **Created**: `nakurity-backend/api/vision.js` - Groq-powered vision LLM API
- **Features**:
  - Analyzes screenshots using Llama Vision model
  - Session-based authentication
  - Rate limiting (10 req/min)
  - Detailed UI element detection
- **Python Client**: `neuro-os/src/regionalization/vision_api_client.py`
  - Automatic session management
  - Heartbeat handling
  - Retry on session expiration

### 4. **Enhanced UI Regionalization**
- **OCR Detection**: Already implemented via EasyOCR in `ocr_detector.py`
  - Detects text, buttons, links, inputs
  - Provides coordinates for clicking
  - Groups elements by type
- **Vision API Integration**: Now optional in `RegionalizationCore`
  - Runs every 20 seconds (less frequent than OCR)
  - Provides AI-powered UI analysis
  - Enhances context with semantic understanding

---

## 📁 File Structure

### Nakurity Backend
```
nakurity-backend/
├── api/
│   ├── session-store.js      # Shared session management
│   ├── session.js             # Session claim/heartbeat/release
│   └── vision.js              # Groq vision API endpoint
├── vercel.json                # Vercel deployment config
└── package.json
```

### Neuro-OS
```
neuro-os/
├── src/
│   ├── regionalization/
│   │   ├── core.py            # Main regionalization system
│   │   ├── ocr_detector.py    # EasyOCR-based UI detection
│   │   └── vision_api_client.py # Nakurity vision API client
│   ├── dev/
│   │   └── neuro_integration/
│   │       └── client.py      # Fixed context message builder
│   └── types/
│       └── neuro_types.py     # Message builder with OCR integration
```

---

## 🔧 Usage

### Starting Neuro-OS with Vision API

```python
# In neuro-os/src/regionalization/core.py
from core import RegionalizationCore

# Enable vision API (optional)
core = RegionalizationCore(enable_vision_api=True)
await core.start()
```

### Context Message Format

Neuro now receives:
```
Screen Resolution: 1920x1080 (coordinates: 0-1919, 0-1079)
Mouse Position: (640, 480)
Text near mouse: "Subscribe"

Active Application: chrome.exe

Detected Text on Screen (127 items):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Share" at (520, 450)
  - "Evil Neuro Glitches" at (400, 200)
  ... and 123 more text items

UI Elements Detected: 45 total

Buttons (12):
  - "Subscribe" at (640, 480)
  - "Like" at (320, 450)
  - "Share" at (520, 450)
  ... more buttons

Visible Windows (3):
  1. Evil Neuro - YouTube [FOCUSED]
     Position: (0, 0), Size: 1920x1080, Click center: (960, 540)
  2. Visual Studio Code
     Position: (100, 100), Size: 800x600, Click center: (500, 400)

AI Vision Analysis:
The screenshot shows a YouTube video page with:
- Video player in center (large area)
- "Subscribe" button (red, top-right of video)
- Like/Dislike buttons below video
- Comment section at bottom
- Sidebar with recommended videos on right
```

---

## 🔐 Security Features

### Session Management
- **Fingerprinting**: Ties sessions to machine (IP + User-Agent hash)
- **Expiration**: 5-minute timeout, extended by heartbeat
- **Automatic Cleanup**: Expired sessions removed periodically
- **Rate Limiting**: 10 requests/minute per IP on vision API

### Authentication Flow
```
neuro-os → GET /api/session/claim
        ← sessionKey: "abc123..."
        
neuro-os → POST /api/session/heartbeat (X-Session-Key: abc123)
        ← success: true

neuro-os → POST /api/neuro-os/vision (X-Session-Key: abc123)
        ← analysis: "..."
        
neuro-os → POST /api/session/release (X-Session-Key: abc123)
        ← success: true
```

---

## 📊 Performance

### OCR Detection
- **Frequency**: Every 2 seconds
- **Elements**: Typically 50-200 per screen
- **Latency**: ~200-500ms per scan

### Vision API
- **Frequency**: Every 20 seconds
- **Latency**: ~2-5 seconds per analysis
- **Cost**: Reduced by infrequent calls

---

## 🚀 Next Steps

### Optional Enhancements
1. **Accessibility API Integration**: Use Windows UIA for semantic UI info
2. **Application-Specific Detectors**: Chrome/YouTube-specific region detection
3. **Caching**: Cache OCR results for unchanged screen regions
4. **Redis Session Store**: Replace in-memory sessions for production scale
5. **Context Compression**: Summarize large context messages to reduce tokens

---

## 🐛 Known Issues

### OCR Limitations
- Requires Tesseract or EasyOCR installation
- May miss UI elements without visible text
- Confidence varies with font/contrast

### Vision API Limitations
- Rate limited (10 req/min)
- Requires Groq API key in backend
- Slower than OCR (2-5s latency)

### Workarounds
- OCR runs locally (no API limits)
- Vision API is optional (enable_vision_api flag)
- Fallback to basic window detection if OCR/vision unavailable

---

## 📝 Configuration

### Enable Vision API in neuro-os
```python
# In src/dev/neuro_integration/client.py
self._reg = RegionalizationCore(enable_vision_api=True)
```

### Set Backend URL
```python
# In src/regionalization/vision_api_client.py
VisionAPIClient(base_url="https://backend.nakurity.com/api")
```

### Configure Groq API Key
```bash
# In nakurity-backend/.env
GROQ_API_KEY=your_groq_api_key_here
```

---

## ✅ Testing

### Test Session Management
```bash
curl https://backend.nakurity.com/api/session/claim
# Returns: {"success": true, "sessionKey": "..."}

curl -X POST https://backend.nakurity.com/api/session/heartbeat \
  -H "X-Session-Key: YOUR_SESSION_KEY"
# Returns: {"success": true}
```

### Test Vision API
```bash
curl -X POST https://backend.nakurity.com/api/neuro-os/vision \
  -H "X-Session-Key: YOUR_SESSION_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_encoded_screenshot", "prompt": "Describe this UI"}'
# Returns: {"success": true, "analysis": "..."}
```

---

## 📖 References

- **Groq Vision API**: https://console.groq.com/docs/vision
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **Neuro-sama API**: https://github.com/VedalAI/neuro-api

---

**Status**: ✅ All improvements implemented and integrated
**Version**: 0.0.2-alpha
**Last Updated**: 2025-01-22
