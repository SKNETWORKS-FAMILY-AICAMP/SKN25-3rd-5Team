from services.retriever import retrieve_category
from services.llm import generate_category_response, parse_category_json

# 카테고리 여행지 추천 
def category_rag(req):
    # 후보 여행지 + 행동 패턴
    result = retrieve_category(req)

    places = result["places"]
    behavior_text = result["behavior_text"]

    raw = generate_category_response(req, places, behavior_text)

    # llm 응답 리스트 변환
    parsed = parse_category_json(raw)

    final = []

    # index 기반 실제 여행지 매칭 
    for item in parsed:
        idx = item.get("index")

        if idx is not None and idx < len(places):
            final.append({
                "title": places[idx]["title"],
                "region": f"{places[idx]['sido']} {places[idx]['sgg']}",
                "tag": item.get("tag", ""),
                "source": places[idx]["source"],
                "description": item.get("description", "")
            })

    # 최종 결과 반환
    return {
        "items": final,
        "raw": raw
    }