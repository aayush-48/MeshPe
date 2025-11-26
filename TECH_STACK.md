# Complete Tech Stack Documentation

## Project Overview
**VoiceWave MeshPay** - A voice-authenticated mesh payment system with Bluetooth Low Energy (BLE) mesh networking capabilities.

---

## 🎨 Frontend Stack

### Core Framework & Build Tools
- **React** `^18.3.1` - UI library
- **TypeScript** `^5.8.3` - Type-safe JavaScript
- **Vite** `^5.4.19` - Build tool and dev server
- **@vitejs/plugin-react-swc** `^3.11.0` - React plugin with SWC compiler for faster builds

### Routing & State Management
- **React Router DOM** `^6.30.1` - Client-side routing
- **@tanstack/react-query** `^5.83.0` - Server state management and data fetching
- **React Context API** - Client-side state management (AuthContext)

### UI Component Libraries
- **Radix UI** - Headless UI primitives:
  - `@radix-ui/react-accordion` `^1.2.11`
  - `@radix-ui/react-alert-dialog` `^1.1.14`
  - `@radix-ui/react-aspect-ratio` `^1.1.7`
  - `@radix-ui/react-avatar` `^1.1.10`
  - `@radix-ui/react-checkbox` `^1.3.2`
  - `@radix-ui/react-collapsible` `^1.1.11`
  - `@radix-ui/react-context-menu` `^2.2.15`
  - `@radix-ui/react-dialog` `^1.1.14`
  - `@radix-ui/react-dropdown-menu` `^2.1.15`
  - `@radix-ui/react-hover-card` `^1.1.14`
  - `@radix-ui/react-label` `^2.1.7`
  - `@radix-ui/react-menubar` `^1.1.15`
  - `@radix-ui/react-navigation-menu` `^1.2.13`
  - `@radix-ui/react-popover` `^1.1.14`
  - `@radix-ui/react-progress` `^1.1.7`
  - `@radix-ui/react-radio-group` `^1.3.7`
  - `@radix-ui/react-scroll-area` `^1.2.9`
  - `@radix-ui/react-select` `^2.2.5`
  - `@radix-ui/react-separator` `^1.1.7`
  - `@radix-ui/react-slider` `^1.3.5`
  - `@radix-ui/react-slot` `^1.2.3`
  - `@radix-ui/react-switch` `^1.2.5`
  - `@radix-ui/react-tabs` `^1.1.12`
  - `@radix-ui/react-toast` `^1.2.14`
  - `@radix-ui/react-toggle` `^1.1.9`
  - `@radix-ui/react-toggle-group` `^1.1.10`
  - `@radix-ui/react-tooltip` `^1.2.7`

### Styling & Design
- **Tailwind CSS** `^3.4.17` - Utility-first CSS framework
- **tailwindcss-animate** `^1.0.7` - Animation utilities
- **@tailwindcss/typography** `^0.5.16` - Typography plugin
- **PostCSS** `^8.5.6` - CSS processing
- **Autoprefixer** `^10.4.21` - CSS vendor prefixing
- **next-themes** `^0.3.0` - Dark mode support
- **class-variance-authority** `^0.7.1` - Component variant management
- **clsx** `^2.1.1` - Conditional class names
- **tailwind-merge** `^2.6.0` - Merge Tailwind classes

### Animation & Visual Effects
- **Framer Motion** `^12.23.24` - Animation library
- **Embla Carousel React** `^8.6.0` - Carousel component

### Form Management & Validation
- **React Hook Form** `^7.61.1` - Form state management
- **@hookform/resolvers** `^3.10.0` - Validation resolvers
- **Zod** `^3.25.76` - Schema validation

### Icons & UI Components
- **Lucide React** `^0.462.0` - Icon library
- **Recharts** `^2.15.4` - Charting library
- **Sonner** `^1.7.4` - Toast notifications
- **cmdk** `^1.1.1` - Command palette
- **input-otp** `^1.4.2` - OTP input component
- **react-day-picker** `^8.10.1` - Date picker
- **react-resizable-panels** `^2.1.9` - Resizable panel layouts
- **vaul** `^0.9.9` - Drawer component

### Utilities
- **date-fns** `^3.6.0` - Date manipulation library

### Development Tools
- **ESLint** `^9.32.0` - Linting
- **TypeScript ESLint** `^8.38.0` - TypeScript linting
- **lovable-tagger** `^1.1.11` - Component tagging (dev tool)

### Browser APIs
- **MediaRecorder API** - Audio recording
- **Web Bluetooth API** - BLE mesh communication
- **FileReader API** - File/blob handling
- **Fetch API** - HTTP requests

---

## 🔧 Backend Stack

### Core Framework
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server for FastAPI
- **Pydantic** - Data validation using Python type annotations

### Audio Processing
- **soundfile** - Audio file I/O (WAV, FLAC, etc.)
- **PyAV (av)** - Audio/video container and codec library (handles WebM/Opus)

### Data Processing
- **NumPy** - Numerical computing library

### Development & Runtime
- **Python 3.10+** - Programming language
- **Virtual Environment (venv)** - Python environment isolation

---

## 🤖 Machine Learning & AI Stack

### Voice Recognition & Processing
- **Resemblyzer** - Voice embedding and speaker verification
  - Uses deep learning models for voiceprint generation
  - VoiceEncoder model for creating voice embeddings
  - Preprocessing utilities for audio normalization

### Speech-to-Text (STT)
- **Faster Whisper** - Optimized Whisper model implementation
  - Model: **Whisper Base** (OpenAI)
  - Device: CPU
  - Compute Type: INT8 (quantized for efficiency)
  - Transcribes audio to text for payment commands

### Natural Language Processing (NLP)
- **Custom Regex-based Parser** (`nlp_parse.py`)
  - Extracts payment amounts from transcribed text
  - Extracts receiver names from commands
  - Extracts action verbs (pay/send)
  - Pattern matching for payment commands

### Voice Biometrics
- **Voiceprint Storage**: NumPy arrays (`.npy` files)
- **Similarity Metric**: Cosine similarity using dot product
- **Verification Threshold**: 0.82 (configurable)

### Liveness Detection
- **Placeholder Implementation** (`liveness.py`)
  - Currently returns `True` (stub for future implementation)

---

## 🔐 Cryptography Stack

### Encryption Libraries
- **PyCryptodome** - Cryptographic library for Python
  - **RSA Encryption** (PKCS1_OAEP padding)
    - Used for encrypting AES session keys
    - Bank public/private key pairs
  - **AES-GCM Encryption** (Advanced Encryption Standard - Galois/Counter Mode)
    - 256-bit keys (32 bytes)
    - 96-bit nonces/IVs (12 bytes)
    - Authenticated encryption with associated data

### Key Management
- **RSA Key Pairs** - Asymmetric encryption
  - Bank private keys stored securely
  - Client public keys for encryption
- **AES Session Keys** - Symmetric encryption
  - Randomly generated per transaction
  - Encrypted with RSA before transmission

### Security Features
- **Hybrid Encryption Scheme**:
  1. Generate random AES session key
  2. Encrypt AES key with bank's RSA public key
  3. Encrypt payment packet with AES-GCM
  4. Transmit encrypted key + encrypted data + authentication tag

---

## 📡 Networking & Communication

### Mesh Networking
- **Bluetooth Low Energy (BLE)** - Mesh network protocol
  - Web Bluetooth API (frontend)
  - Service UUID: `12345678-1234-1234-1234-123456789abc`
  - Characteristic UUID: `87654321-4321-4321-4321-cba987654321`
  - Peer-to-peer encrypted packet transmission

### HTTP/REST API
- **FastAPI REST Endpoints**:
  - `/enroll/*` - Voice enrollment
  - `/auth/*` - Authentication & user management
  - `/stt/*` - Speech-to-text processing
  - `/payment/*` - Payment processing
  - `/encrypt/*` - Encryption services

### CORS Configuration
- **CORS Middleware** - Cross-origin resource sharing
  - Development: Allows all origins (`*`)
  - Credentials enabled
  - All methods and headers allowed

---

## 💾 Data Storage

### File System Storage
- **JSON Files** (`users.json`) - User data storage
  - User profiles
  - Contact lists
  - Account information

### Voiceprint Storage
- **NumPy Arrays** (`.npy` files)
  - Location: `ml/models/stored_voiceprints/`
  - Format: Binary NumPy arrays
  - One file per user: `{user_id}.npy`

### Key Storage
- **RSA Key Files** - Bank private/public keys
  - Stored in `backend/crypto/` directory

---

## 🛠️ Development Tools & Utilities

### Frontend Dev Tools
- **Vite Dev Server** - Development server (port 8080)
- **Hot Module Replacement (HMR)** - Live reloading
- **TypeScript Compiler** - Type checking
- **ESLint** - Code linting

### Backend Dev Tools
- **Uvicorn** - Development server (port 8000)
- **FastAPI Auto Documentation** - Swagger/OpenAPI docs
- **Python Virtual Environment** - Dependency isolation

### Build & Deployment
- **Vite Build** - Production build tool
- **TypeScript Compilation** - Type checking and transpilation
- **PostCSS Processing** - CSS optimization

---

## 📦 Package Managers

- **npm** / **package-lock.json** - Frontend dependencies
- **pip** / **requirements.txt** - Backend dependencies
- **Bun** (optional) - Alternative package manager (lockfile present)

---

## 🌐 Browser Compatibility

### Required Browser Features
- **MediaRecorder API** - Audio recording
- **Web Bluetooth API** - BLE mesh networking
- **Fetch API** - HTTP requests
- **FileReader API** - File handling
- **ES6+ JavaScript** - Modern JavaScript features

### Supported Browsers
- Chrome/Edge (full support)
- Firefox (limited Web Bluetooth support)
- Safari (limited Web Bluetooth support)

---

## 🔄 Data Flow Architecture

1. **Audio Capture** → MediaRecorder API (WebM/Opus)
2. **Audio Processing** → PyAV/soundfile → NumPy arrays
3. **Voice Enrollment** → Resemblyzer → Voiceprint embedding
4. **Voice Verification** → Cosine similarity comparison
5. **Speech Recognition** → Faster Whisper → Text transcription
6. **NLP Parsing** → Regex patterns → Structured payment data
7. **Encryption** → RSA + AES-GCM → Encrypted packet
8. **Mesh Transmission** → BLE → Peer devices
9. **Decryption** → Bank private key → Payment processing

---

## 📊 Model Specifications

### Voice Encoder (Resemblyzer)
- **Input**: 16kHz mono audio
- **Output**: 256-dimensional embedding vector
- **Preprocessing**: VAD (Voice Activity Detection) disabled
- **Similarity**: Cosine similarity (dot product normalized)

### Whisper Model
- **Model Size**: Base
- **Quantization**: INT8
- **Device**: CPU
- **Input**: 16kHz float32 audio
- **Output**: Transcribed text

### Voiceprint Format
- **Type**: NumPy array (float32)
- **Dimensions**: 256
- **Storage**: Binary `.npy` format
- **Size**: ~1KB per voiceprint

---

## 🔒 Security Features

1. **Voice Biometric Authentication** - Speaker verification
2. **Hybrid Encryption** - RSA + AES-GCM
3. **Authenticated Encryption** - GCM mode with authentication tags
4. **Challenge-Response** - Random word challenges for login
5. **Secure Key Storage** - Private keys stored securely
6. **TTL (Time-To-Live)** - Packet expiration (60 seconds default)

---

## 📝 Additional Notes

- **Audio Format**: WebM/Opus (frontend) → Converted to WAV/float32 (backend)
- **Sample Rate**: 16kHz (standard for voice processing)
- **Challenge Words**: ["apple", "neon", "matrix", "secure", "galaxy", "mesh", "ocean", "binary"]
- **Payment Command Patterns**: "pay [receiver] [amount]", "send [receiver] [amount]"
- **Development Ports**: Frontend (8080), Backend (8000)

---

## 🚀 Deployment Considerations

### Frontend
- Static site hosting (Vite build output)
- CDN deployment possible
- Requires HTTPS for Web Bluetooth API

### Backend
- ASGI server (Uvicorn/Gunicorn)
- Python 3.10+ required
- ML models loaded at startup
- File system storage for voiceprints

### Infrastructure
- No database required (file-based storage)
- Stateless API design
- Horizontal scaling possible with shared storage

---

*Last Updated: Based on current codebase analysis*

