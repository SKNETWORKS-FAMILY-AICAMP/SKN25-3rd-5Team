from fastapi import FastAPI
import os
import psycopg2
import pandas as pd
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )


def create_tables():
    """PostgreSQL 테이블 생성 (정확한 컬럼 정의서에 맞춤)"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1️⃣ 여행지 데이터 (관광지, 반려동물, 무장애)
            cur.execute("""
                DROP TABLE IF EXISTS travel_places CASCADE;
                CREATE TABLE travel_places (
                    place_id SERIAL PRIMARY KEY,
                    source VARCHAR(50) NOT NULL,        -- 'regional' / 'barrier_free' / 'pet'
                    title VARCHAR(255) NOT NULL,        -- 관광지 명
                    content_type_nm VARCHAR(100),       -- 관광지 유형 명
                    sido_nm VARCHAR(50),                -- 시도 명
                    sgg_nm VARCHAR(50),                 -- 시군구 명
                    zipcode VARCHAR(20),                -- 시군구 코드 (반려동물/무장애)
                    latitude FLOAT,                     -- 위도
                    longitude FLOAT,                    -- 경도
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 2️⃣ 행동 패턴 데이터 (설문조사)
            cur.execute("""
                DROP TABLE IF EXISTS user_behavior CASCADE;
                CREATE TABLE user_behavior (
                    behavior_id SERIAL PRIMARY KEY,
                    with_pet BOOLEAN,                   -- 반려동물 동반 여부 (N은 False)
                    gender VARCHAR(20),                 -- 성별
                    age_group VARCHAR(20),              -- 나이 그룹
                    trip_visit_area VARCHAR(20),        -- 방문지역 시군구 코드
                    trip_stay_area VARCHAR(20),         -- 숙박지역 시군구 코드
                    trip_stay_type VARCHAR(100),        -- 숙박지역 유형
                    trip_transport_city2city VARCHAR(50), -- 지역간 이동 교통수단
                    trip_transport_incity VARCHAR(50),   -- 지역내 이동 교통수단 1
                    trip_transport_incity2 VARCHAR(50),  -- 지역내 이동 교통수단 2
                    companion_type VARCHAR(100),        -- 동반자 유형
                    travel_activity VARCHAR(100),       -- 활동 유형
                    trip_visit_sido VARCHAR(50),        -- 방문지역 시도 명
                    trip_visit_sigungu VARCHAR(50),     -- 방문지역 시군구 명
                    trip_stay_sido VARCHAR(50),         -- 숙박지역 시도 명
                    trip_stay_sigungu VARCHAR(50),      -- 숙박지역 시군구 명
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        
        conn.commit()
        print("테이블 생성 완료")
        return True
    except Exception as e:
        print(f"테이블 생성 실패: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def load_pickle_data():
    """Pickle 파일을 DB에 로드"""
    data_dir = BASE_DIR / "data"
    
    print("\n📂 Pickle 파일 로드 중...")
    
    try:
        df_regional = pd.read_pickle(data_dir / "tourpoi.pkl")
        df_barrier_free = pd.read_pickle(data_dir / "barrier_free.pkl")
        df_pet = pd.read_pickle(data_dir / "pet_df_final.pkl")
        df_behavior = pd.read_pickle(data_dir / "tour_survey_final.pkl")
        
        print(f"  ✓ 관광지: {len(df_regional)} 행")
        print(f"  ✓ 무장애 여행지: {len(df_barrier_free)} 행")
        print(f"  ✓ 반려동물 여행지: {len(df_pet)} 행")
        print(f"  ✓ 행동 패턴: {len(df_behavior)} 행")
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return False
    
    print("\n🔄 데이터 정제 및 매핑 중...")
    
    # 여행지 데이터 정제
    for df, source_name in [
        (df_regional, 'regional'),
        (df_barrier_free, 'barrier_free'),
        (df_pet, 'pet')
    ]:
        # 컬럼명 정규화 (필요시)
        df['source'] = source_name
        # title, content_type_nm, sido_nm, sgg_nm, latitude, longitude, zipcode는 그대로 사용
    
    # 행동 패턴 데이터 정제
    # 결측치를 'N'으로 대치
    for col in df_behavior.columns:
        if df_behavior[col].dtype == 'object':
            df_behavior[col] = df_behavior[col].fillna('N')
        else:
            df_behavior[col] = df_behavior[col].fillna(False)
    
    # with_pet 컬럼: 'N'은 False, 그 외는 True로 변환
    if 'with_pet' in df_behavior.columns:
        df_behavior['with_pet'] = df_behavior['with_pet'].apply(
            lambda x: False if x == 'N' else True
        )
    
    print("\n💾 DB에 저장 중...")
    conn = get_connection()
    
    saved_count = 0
    
    try:
        # 여행지 데이터 로드
        for source_name, df in [
            ('regional', df_regional),
            ('barrier_free', df_barrier_free),
            ('pet', df_pet)
        ]:
            with conn.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        cur.execute("""
                            INSERT INTO travel_places (
                                source, title, content_type_nm, sido_nm, 
                                sgg_nm, zipcode, latitude, longitude
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            source_name,
                            str(row.get('title', 'Unknown'))[:255],
                            str(row.get('content_type_nm', ''))[:100] if pd.notna(row.get('content_type_nm')) else None,
                            str(row.get('sido_nm', ''))[:50] if pd.notna(row.get('sido_nm')) else None,
                            str(row.get('sgg_nm', ''))[:50] if pd.notna(row.get('sgg_nm')) else None,
                            str(row.get('zipcode', ''))[:20] if pd.notna(row.get('zipcode')) else None,
                            float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                            float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                        ))
                        saved_count += 1
                    except Exception as row_err:
                        pass
            
            conn.commit()
            print(f"  ✓ {source_name} 로드 완료")
        
        # 행동 패턴 데이터 로드
        with conn.cursor() as cur:
            for _, row in df_behavior.iterrows():
                try:
                    cur.execute("""
                        INSERT INTO user_behavior (
                            with_pet, gender, age_group, trip_visit_area,
                            trip_stay_area, trip_stay_type, trip_transport_city2city,
                            trip_transport_incity, trip_transport_incity2, companion_type,
                            travel_activity, trip_visit_sido, trip_visit_sigungu,
                            trip_stay_sido, trip_stay_sigungu
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row.get('with_pet'),
                        str(row.get('gender', 'N'))[:20],
                        str(row.get('age_group', 'N'))[:20],
                        str(row.get('trip_visit_area', 'N'))[:20],
                        str(row.get('trip_stay_area', 'N'))[:20],
                        str(row.get('trip_stay_type', 'N'))[:100],
                        str(row.get('trip_transport(city2city)', 'N'))[:50],
                        str(row.get('trip_transport(incity)', 'N'))[:50],
                        str(row.get('trip_transport(incity)2', 'N'))[:50],
                        str(row.get('companion_type', 'N'))[:100],
                        str(row.get('travel_activity', 'N'))[:100],
                        str(row.get('trip_visit_sido', 'N'))[:50],
                        str(row.get('trip_visit_sigungu', 'N'))[:50],
                        str(row.get('trip_stay_sido', 'N'))[:50],
                        str(row.get('trip_stay_sigungu', 'N'))[:50],
                    ))
                    saved_count += 1
                except Exception as row_err:
                    pass
        
        conn.commit()
        print(f"  ✓ 행동 패턴 로드 완료")
        
        print(f"\n✅ 총 {saved_count}개 레코드 저장 완료!")
        return True
    except Exception as e:
        print(f"❌ 데이터 삽입 실패: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


@app.get("/")
def root():
    return {"message": "Backend is running"}



@app.post("/init-db")
def init_database():
    """데이터베이스 초기화 및 데이터 로드"""    
    if create_tables():
        if load_pickle_data():
            return {
                "status": "success",
                "message": "데이터베이스 초기화 및 데이터 로드 완료"
            }
        else:
            return {
                "status": "error",
                "message": "데이터 로드 실패"
            }
    else:
        return {
            "status": "error",
            "message": "테이블 생성 실패"
        }


@app.get("/data-status")
def data_status():
    """로드된 데이터 상태 확인"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # 테이블 존재 확인
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
                    "message": "데이터가 아직 로드되지 않았습니다. /init-db 엔드포인트를 호출하세요.",
                    "travel_places": [],
                    "user_behavior": {"total_records": 0}
                }
            
            # 여행지 통계 (source별)
            cur.execute("""
                SELECT 
                    source,
                    COUNT(*) as count
                FROM travel_places
                GROUP BY source
                ORDER BY source
            """)
            places_stats = cur.fetchall()
            
            # 행동 패턴 통계
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


