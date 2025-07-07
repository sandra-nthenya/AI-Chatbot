from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid
import os
from sqlalchemy.orm import Session
from database import get_db
from rag_service import rag_service
from llm_service import llm_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Chat Support API",
    description="Backend API for AI Chat Support Widget",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class Message(BaseModel):
    id: Optional[str] = None
    session_id: str
    sender: str  # 'user' or 'bot'
    content: str
    timestamp: Optional[datetime] = None

class ChatSession(BaseModel):
    session_id: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str

# In-memory storage (replace with database)
sessions = {}
messages = {}

@app.get("/")
async def root():
    return {"message": "AI Chat Support API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get AI response using RAG and LLM"""
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Store user message
    user_message = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        sender="user",
        content=request.message,
        timestamp=datetime.utcnow()
    )
    messages[session_id] = messages.get(session_id, []) + [user_message]
    
    # Use RAG to find relevant context
    tenant_id = request.tenant_id or "default"
    relevant_chunks = rag_service.search_similar_chunks(db, request.message, tenant_id, limit=3)
    
    # Generate context-aware prompt
    context_prompt = rag_service.generate_context_prompt(request.message, relevant_chunks)
    
    # Generate AI response using LLM
    try:
        bot_response = await llm_service.generate_response(request.message, context_prompt)
    except Exception as e:
        print(f"LLM error: {e}")
        bot_response = f"Thanks for your message: '{request.message}'. This is a fallback response."
    
    # Store bot response
    bot_message = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        sender="bot",
        content=bot_response,
        timestamp=datetime.utcnow()
    )
    messages[session_id] = messages.get(session_id, []) + [bot_message]
    
    # Update session
    sessions[session_id] = ChatSession(
        session_id=session_id,
        tenant_id=request.tenant_id,
        created_at=sessions.get(session_id, {}).get('created_at', datetime.utcnow()),
        last_activity=datetime.utcnow()
    )
    
    return ChatResponse(message=bot_response, session_id=session_id)

@app.get("/chat/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str):
    """Get chat history for a session"""
    if session_id not in messages:
        raise HTTPException(status_code=404, detail="Session not found")
    return messages[session_id]

@app.post("/sessions")
async def create_session(tenant_id: Optional[str] = None):
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = ChatSession(
        session_id=session_id,
        tenant_id=tenant_id,
        created_at=datetime.utcnow(),
        last_activity=datetime.utcnow()
    )
    messages[session_id] = []
    return {"session_id": session_id}

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = "default",
    db: Session = Depends(get_db)
):
    """Upload and process a knowledge document"""
    try:
        # Validate file type
        allowed_types = [".txt", ".pdf", ".doc", ".docx"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
        
        # Read file content (simplified - in production, use proper text extraction)
        content = await file.read()
        if file_ext == ".txt":
            text_content = content.decode('utf-8')
        else:
            # For other file types, you'd use libraries like PyPDF2, python-docx, etc.
            text_content = f"Content from {file.filename} (processing not implemented for {file_ext})"
        
        # Create document record
        from models import KnowledgeDocument
        document = KnowledgeDocument(
            tenant_id=tenant_id,
            filename=file.filename,
            file_path=f"uploads/{file.filename}",
            file_type=file_ext,
            file_size=len(content),
            is_processed=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document with RAG
        success = rag_service.process_document(db, document.id, text_content)
        
        if success:
            return {
                "message": "Document uploaded and processed successfully",
                "document_id": document.id,
                "filename": file.filename
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/llm/status")
async def get_llm_status():
    """Get status of available LLM models"""
    return llm_service.get_available_models()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 