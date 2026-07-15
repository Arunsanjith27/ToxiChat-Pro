# Dependency Tree & Technical Stack

ToxiChat relies on a deeply integrated stack of Python and Node.js dependencies, heavily biased toward Machine Learning and real-time networking.

## Backend (Python 3.10+)

The backend environment is defined in `backend/requirements.txt`.

### Web & API Framework
- **`fastapi` (0.135+)**: High-performance REST and WebSocket framework.
- **`uvicorn` (0.44+)**: The ASGI web server implementation powering FastAPI.
- **`websockets` (16.0)**: Underlying WebSocket implementation utilized by Starlette/FastAPI.

### Database & Caching
- **`motor` (3.7+)**: The official asynchronous Python driver for MongoDB.
- **`pymongo` (4.16+)**: Synchronous MongoDB driver (underpins `motor`).
- **`redis` (8.0+)**: Used primarily for rate limiting, locking, and Pub/Sub across WebSocket workers.

### Authentication & Security
- **`python-jose`**: Used to generate and verify JWT (`HS256`) tokens statelessly.
- **`bcrypt` & `passlib`**: Cryptographic hashing for user passwords.
- **`python-dotenv`**: Environment variable injection.

### Machine Learning & AI
This is the heaviest portion of the dependency tree.
- **`torch` (2.12+)**: PyTorch, the underlying tensor framework required by HuggingFace and EasyOCR.
- **`transformers` (5.6+)**: HuggingFace library used to load RoBERTa toxicity models and summarization models.
- **`onnxruntime`**: Used by `nudenet` to execute Vision models without requiring PyTorch overhead.
- **`scikit-learn` & `scipy`**: Used by the conversation analytics engine to calculate risk distributions and clustering.
- **`pillow` (PIL)**: Image manipulation prior to OCR/Vision scanning.
- **`sentence-transformers`** (implicit via `transformers`): Used for embedding generation.

### Reporting & Media
- **`reportlab` (5.0+)**: Used to generate the cryptographic PDF compliance reports.
- **`pydub`**: Used in conjunction with system `ffmpeg` to parse audio durations and validate file integrity for the `faster-whisper` pipeline.

## Frontend (React 18)

The frontend is a `create-react-app` architecture defined in `frontend/package.json`.

### Core UI Framework
- **`react` & `react-dom` (18.2+)**: Component architecture and virtual DOM.
- **`react-router-dom` (6.20+)**: Client-side routing for nested dashboard and chat views.

### Styling & Aesthetics
- **`tailwindcss` (3.4+)**: Utility-first CSS generation.
- **`postcss` & `autoprefixer`**: Build tools for CSS compatibility.
- **`lucide-react`**: Standardized vector iconography library.
- **`framer-motion`**: Used for the micro-animations (e.g., the pop-in effect of the Pre-Send AI Warning Modal).

### 3D Rendering (Experimental/Dashboard)
- **`three` (0.183+)**: WebGL 3D rendering engine.
- **`@react-three/fiber` & `@react-three/drei`**: React wrappers for Three.js, utilized in the 3D admin analytics visualization views.

### Data Visualization
- **`recharts`**: Used across the Admin Dashboard and Conversation Intelligence panels to render line charts (Risk Velocity) and pie charts (Emotion Distribution).
