# AI Chat Support Bot

A full-stack AI Chat Support Bot that can be embedded into websites as a chat widget. Features a React frontend with theme support and a FastAPI backend with RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Features

### Frontend (React + TypeScript)
- **Floating Chat Widget**: Customizable chat bubble with smooth animations
- **Theme Support**: Light/dark mode with automatic system detection
- **Responsive Design**: Works on desktop and mobile devices
- **Session Management**: Anonymous and authenticated user support
- **Real-time Chat**: Live message exchange with AI responses

### Backend (FastAPI + PostgreSQL/Supabase)
- **RAG Integration**: Document processing and semantic search
- **Multi-LLM Support**: Gemini, OpenAI, and fallback options
- **Multi-tenant Architecture**: Isolated data per organization
- **Document Upload**: Process PDFs, TXT, DOC files for knowledge base
- **Session Management**: Persistent chat history
- **RESTful API**: Clean, documented endpoints

## 📁 Project Structure

```
ai chat bot/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # Chat widget components
│   │   ├── services/         # API integration
│   │   └── ...
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── rag_service.py       # RAG implementation
│   ├── llm_service.py       # LLM integration
│   ├── database.py          # Database connection
│   ├── config.py            # Configuration management
│   └── requirements.txt     # Python dependencies
└── README.md
```

## 🛠️ Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- (Optional) Supabase account for production database

### 1. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-basic.txt  # For basic functionality
# OR
pip install -r requirements.txt  # For full RAG/LLM features
```

### 3. Database Setup

#### Option A: SQLite (Development)
```bash
cd backend
python database.py
```

#### Option B: Supabase (Production)
1. Create a Supabase project at https://supabase.com
2. Copy `.env.template` to `.env` and fill in your credentials
3. Run: `python supabase_setup.py`

### 4. Start Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/chat_support
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# API Keys
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# RAG Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Frontend Configuration

Set the API URL in `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

## 📚 API Endpoints

### Chat Endpoints
- `POST /chat` - Send message and get AI response
- `GET /chat/{session_id}/messages` - Get chat history
- `POST /sessions` - Create new chat session
- `GET /sessions/{session_id}` - Get session details

### Document Management
- `POST /documents/upload` - Upload knowledge documents
- `GET /llm/status` - Check LLM service status

### Health Check
- `GET /health` - API health status

## 🎨 Customization

### Frontend Widget

The chat widget can be customized with props:

```typescript
<ChatWidget 
  theme="auto"  // 'light' | 'dark' | 'auto'
/>
```

### Styling

Modify CSS variables in `frontend/src/index.css`:

```css
.chat-theme-light {
  --chat-bg: #fff;
  --chat-header-bg: linear-gradient(135deg, #4f8cff 60%, #3358e0 100%);
  /* ... more variables */
}
```

### Backend Configuration

Adjust RAG settings in `backend/config.py`:

```python
chunk_size: int = 1000
chunk_overlap: int = 200
embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
```

## 🔌 Integration

### Embedding the Widget

Add the chat widget to any website:

```html
<script type="module">
  import ChatWidget from './path/to/ChatWidget.jsx';
  
  // Render the widget
  ReactDOM.render(<ChatWidget />, document.getElementById('chat-widget'));
</script>
```

### API Integration

```javascript
// Send a message
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    session_id: 'user-session-123',
    tenant_id: 'my-organization'
  })
});

const data = await response.json();
console.log(data.message); // AI response
```

## 🚀 Deployment

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy the dist/ folder to your hosting service
```

### Backend Deployment

1. **Docker** (Recommended):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Direct Deployment**:
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Environment Setup

For production, ensure:
- Database connection is configured
- API keys are set
- CORS origins are restricted
- File upload directory is writable
