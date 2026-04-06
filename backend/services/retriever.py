import os
from sqlalchemy import create_engine, text

class RetrieverService:
    def __init__(self):
        # 환경 변수에서 DB 연결 정보 로드
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
        self.engine = create_engine(db_url)

    def get_relevant_context(self, query_vector: list, region_filter: str = None, is_pet: bool = False, is_bf: bool = False) -> str:
        params = {"vector": str(query_vector), "limit": 8}
        
        # 1. 가중치 점수 설정 (True면 1, False면 0)
        pet_val = 1 if is_pet else 0
        bf_val = 1 if is_bf else 0
        
        # 지역 필터 처리
        region_clause = "1=1"
        if region_filter:
            reg = region_filter[0] if isinstance(region_filter, list) else region_filter
            region_clause = "sido_nm LIKE :region"
            params["region"] = f"%{reg}%"

        # 2. 지능형 랭킹 SQL
        # - 1순위: 반려동물/무장애 데이터 소스가 일치하는가?
        # - 2순위: 사용자가 언급한 지역인가?
        # - 3순위: 의미론적 유사도(Distance)가 얼마나 가까운가?
        sql = f"""
            SELECT title, sido_nm, sgg_nm, source,
                   (embedding <=> :vector) as distance
            FROM travel_place_vectors
            ORDER BY 
                (CASE WHEN source = 'pet' AND {pet_val} = 1 THEN 0 ELSE 1 END),
                (CASE WHEN source = 'barrier_free' AND {bf_val} = 1 THEN 0 ELSE 1 END),
                (CASE WHEN {region_clause} THEN 0 ELSE 1 END),
                distance
            LIMIT :limit
        """
        
        with self.engine.connect() as conn:
            results = conn.execute(text(sql), params).mappings().all()
            
            # 검색 결과가 부족할 경우를 대비한 최소한의 유사도 검색(Fallback)
            if not results:
                fallback_sql = "SELECT title, sido_nm, sgg_nm, source FROM travel_place_vectors ORDER BY embedding <=> :vector LIMIT 5"
                results = conn.execute(text(fallback_sql), {"vector": params["vector"]}).mappings().all()

        # 결과 텍스트 조립
        context_list = []
        for r in results:
            tag = "🐾 반려동물 동반" if r['source'] == 'pet' else "♿ 무장애시설" if r['source'] == 'barrier_free' else "📍 일반"
            context_list.append(f"- {r['title']} ({r['sido_nm']} {r['sgg_nm']}) [{tag}]")
            
        return "\n".join(context_list) if context_list else "관련 정보를 찾을 수 없습니다."