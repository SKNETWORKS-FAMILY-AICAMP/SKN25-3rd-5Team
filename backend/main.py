from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from services.rag import RAGService

app = FastAPI()
rag_service = RAGService()

class QueryRequest(BaseModel):
    page_type: str
    question: str
    session_id: Optional[str] = "default_user"
    chat_history: Optional[List[dict]] = []

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    try:
        # 인자 순서: session_id, mode, question 순서 엄수
        answer = rag_service.process_query(
            session_id=request.session_id,
            mode=request.page_type, 
            question=request.question,
            chat_history=request.chat_history
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Backend is running"}