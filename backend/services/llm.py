from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import json
import re


# 모델
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 임베딩 함수 
def get_embedding(text):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding


# category 여행지 추천 
def generate_category_response(req, docs, behavior_text):

    context = "\n".join([
        f"{i}. {d['title']} ({d['sido']} {d['sgg']})"
        for i, d in enumerate(docs)
    ])

    # 프롬프트 
    prompt = f"""
    너는 여행 추천 시스템이다.

    사용자 조건:
    - 목적지: {req.destination}
    - 이동 수단: {req.transportation}
    - 동행자: {req.companion}

    사용자와 유사한 여행 패턴:
    {behavior_text}

    아래 후보 중에서만 선택해서 추천해:

    {context}

    규칙:
    - 반드시 후보 번호(index)만 사용
    - 새로운 여행지 만들지 말 것
    - 관련된 여행 유형 작성할 것

    출력(JSON):

    [
      {{
        "index": 0,
        "tag": "활동 유형",
        "description": "추천 이유"
      }}
    ]
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content




def generate_plan_with_rag(req, data):

    behavior = data["behavior"]
    places = data["places"]

    # 행동 패턴 텍스트
    behavior_text = "\n".join([
        f"{b[2]} / 이동: {b[3]}"
        for b in behavior
    ])

    # 여행지 후보
    place_text = "\n".join([
        f"- {p[0]} ({p[1]} {p[2]}) [{p[3]}]"
        for p in places
    ])

    prompt = f"""
너는 여행 일정 플래너다.

조건:
- 출발지: {req.departure}
- 목적지: {req.destination}
- 이동 수단: {req.transportation}

사용자 행동 패턴:
{behavior_text}

추천 여행지:
{place_text}

규칙:
- JSON 형식으로 출력하지 마라
- "활동:" 같은 형식 사용하지 마라
- 자연스러운 여행 일정 문장으로 작성
- 사람이 여행 계획 짜듯이 작성

출력 형식:

1일차
09:00 관덕정에서 산책하며 여행 시작
12:30 메타포에서 점심 식사
15:00 부용정에서 여유로운 휴식
18:00 사직단에서 저녁 산책

2일차
...


"""

    res = llm.invoke([HumanMessage(content=prompt)])
    return res.content



# LLM 응답 변환 
def parse_category_json(text):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except:
        return []
    