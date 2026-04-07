import psycopg2
from services.llm import get_embedding
import os

# DB
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )

# 카테고리 여행지 추천
def retrieve_category(req):

    # embedding용 문장
    query_text = f"""
        {req.destination}에서 출발하는
        {req.purpose} 여행
        {req.companion}와 함께하는 여행
        {req.transportation} 이용
    """

    # 벡터 변환
    query_embedding = get_embedding(query_text)

    conn = get_connection()
    cur = conn.cursor()

    # 여행지 (결과 후보)
    cur.execute("""
        SELECT 
            title,
            sido_nm,
            content_type_nm,
            sgg_nm,
            source,
            embedding <-> %s::vector AS distance
        FROM travel_place_vectors
        WHERE content_type_nm = %s
        AND sido_nm = %s
        ORDER BY embedding <-> %s::vector
        LIMIT 20
    """, (query_embedding, req.purpose, req.destination, query_embedding))

    places = cur.fetchall()

    # 행동 패턴 
    cur.execute("""
        SELECT 
            trip_visit_sido,
            trip_visit_sigungu,
            travel_activity,
            companion_type
        FROM user_behavior_vectors
        WHERE trip_visit_sido = %s
        LIMIT 20
    """, (req.destination,))

    behavior = cur.fetchall()

    cur.close()
    conn.close()

    # 여행지 후보 dict 형태 변환
    place_results = [
        {
            "title": row[0],
            "sido": row[1],
            "type": row[2],
            "sgg": row[3],
            "source": row[4]
        }
        for row in places
    ]

    behavior_text = "\n".join([
        f"{row[0]} {row[1]}에서 {row[2]} 활동, 동행자: {row[3]}"
        for row in behavior
    ]) 

    # 결과 반환
    return {
        "places": place_results,
        "behavior_text": behavior_text
    }



def retrieve_plan(req):

    conn = get_connection()
    cur = conn.cursor()

    # 행동패턴 
    cur.execute("""
        SELECT 
            trip_visit_sido,
            trip_visit_sigungu,
            travel_activity,
            trip_transport_incity
        FROM user_behavior_vectors
        WHERE trip_visit_sido = %s
        LIMIT 5
    """, (req.destination,))

    behavior = cur.fetchall()

    #  여행지 후보 
    cur.execute("""
        SELECT 
            title,
            sido_nm,
            sgg_nm,
            content_type_nm
        FROM travel_place_vectors
        WHERE sido_nm = %s
        LIMIT 10
    """, (req.destination,))

    places = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "behavior": behavior,
        "places": places
    }