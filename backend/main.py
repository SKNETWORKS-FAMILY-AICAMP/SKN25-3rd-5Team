import os
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/data-status")
def data_status():
    """로드된 데이터 상태 확인"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'travel_places'
                )
            """)
            places_table_exists = cur.fetchone()[0]
            
            if not places_table_exists:
                return {
                    "status": "empty",
                    "message": "데이터가 아직 로드되지 않았습니다.",
                    "travel_places": [],
                    "user_behavior": {"total_records": 0}
                }
            
            cur.execute("""
                SELECT 
                    source,
                    COUNT(*) as count
                FROM travel_places
                GROUP BY source
                ORDER BY source
            """)
            places_stats = cur.fetchall()
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN with_pet = true THEN 1 END) as with_pet_count,
                    COUNT(DISTINCT age_group) as age_groups,
                    COUNT(DISTINCT gender) as genders
                FROM user_behavior
            """)
            behavior_stats = cur.fetchone()
        
        conn.close()
        
        return {
            "status": "ok",
            "travel_places": [
                {
                    "source": row[0],
                    "total": row[1]
                }
                for row in places_stats
            ],
            "user_behavior": {
                "total_records": behavior_stats[0] if behavior_stats else 0,
                "with_pet": behavior_stats[1] if behavior_stats else 0,
                "age_groups": behavior_stats[2] if behavior_stats else 0,
                "genders": behavior_stats[3] if behavior_stats else 0
            }
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# 카테고리 여행지 추천
from services.rag import category_rag, chat_rag 
class RecommendRequest(BaseModel):
    destination: str
    purpose: str
    transportation: str
    companion: List[str]
    duration: int


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    limit: int = 5

@app.post("/recommend")
def recommend(req: RecommendRequest):
    results = category_rag(req)
    return {"results": results}


@app.post("/chat")
def chat(req: ChatRequest):
    result = chat_rag(
        message=req.message,
        history=req.history,
        limit=req.limit,
    )
    return result


# 일정 생성
from services.rag import plan_rag 
class PlanRequest(BaseModel):
    departure: str
    destination: str
    travel_type: str
    transportation: str
    departure_time: int



@app.post("/plan")
def plan(req: PlanRequest):
    result = plan_rag(req)   
    return {"result": result}
