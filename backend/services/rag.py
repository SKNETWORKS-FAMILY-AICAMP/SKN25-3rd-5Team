import json
import re
from services.llm import LLMService
from services.retriever import RetrieverService

class RAGService:
    def __init__(self):
        self.llm = LLMService()
        self.retriever = RetrieverService()
        self.user_states = {}

    def _get_or_update_state(self, session_id: str, question: str):
        if session_id not in self.user_states:
            self.user_states[session_id] = {
                "region": None, "pet": False, "barrier_free": False, "companion": None
            }
        
        analysis_prompt = f"""
        질문: {question}
        위 질문에서 다음 정보를 JSON으로 추출해. (없으면 null)
        - region: 도시명
        - pet: 반려동물/강아지/고양이와 함께하는 여행이면 true
        - barrier_free: 휠체어/어르신 등 무장애 여행이면 true
        - companion: 누구와 함께 가는지(가족, 연인 등)
        """
        
        try:
            res = self.llm.get_response([{"role": "user", "content": analysis_prompt}])
            match = re.search(r'\{.*\}', res, re.DOTALL)
            if match:
                intent = json.loads(match.group())
                state = self.user_states[session_id]
                # 기존 정보 유지하며 새 정보 업데이트
                if intent.get("region"): state["region"] = str(intent["region"])
                if intent.get("pet") is True: state["pet"] = True
                if intent.get("barrier_free") is True: state["barrier_free"] = True
                if intent.get("companion"): state["companion"] = str(intent["companion"])
        except:
            pass
        return self.user_states[session_id]

    def process_query(self, session_id: str, mode: str, question: str, chat_history: list = None) -> str:
        try:
            state = self._get_or_update_state(session_id, question)
            
            # [똑똑한 검색어 생성] 
            # 단순 질문에 '반려동물 동반', '강아지' 등의 유의어를 섞어 검색 품질을 높입니다.
            enriched_terms = []
            if state["pet"]: enriched_terms.append("강아지 고양이 반려동물 동반 가능 펫프렌들리 장소")
            if state["region"]: enriched_terms.append(str(state["region"]))
            enriched_terms.append(str(question))
            
            final_query = " ".join([str(t) for t in enriched_terms if t])
            query_vector = self.llm.get_embedding(final_query)
            
            # DB 검색 (가중치 기반 정렬 적용된 Retriever 호출)
            context = self.retriever.get_relevant_context(
                query_vector=query_vector,
                region_filter=state["region"],
                is_pet=state["pet"],
                is_bf=state["barrier_free"]
            )

            # AI 최종 답변 생성
            system_prompt = f"너는 {state['companion'] if state['companion'] else '사용자'}와 {'반려동물' if state['pet'] else ''} 여행을 돕는 전문 가이드야."
            messages = [{"role": "system", "content": system_prompt}]
            if chat_history:
                messages.extend(chat_history[-5:])
            messages.append({"role": "user", "content": f"참고 데이터:\n{context}\n\n질문: {question}"})
            
            return self.llm.get_response(messages)
            
        except Exception as e:
            return f"RAG 오류: {str(e)}"