import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        
        # 요청하신 모델명으로 설정
        self.model = "gpt-5-mini" 
        self.embed_model = "text-embedding-3-small"

        # 시스템 프롬프트: 제약 조건 준수 강조
        self.PROMPT_CHAT = """
역할: 사용자 맞춤형 여행 전문 가이드
지침:
1. 사용자가 '반려동물(pet)'이나 '부모님/거동 불편(barrier_free)' 조건을 언급했다면, 반드시 제공된 '참고 데이터' 중 해당 조건이 일치하는 정보(출처 확인)만 사용하세요.
2. 이전 대화 맥락(지역, 동반자 정보 등)을 끝까지 유지하여 답변하세요.
3. 데이터에 없는 내용을 지어내지 마세요.
"""

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(input=text, model=self.embed_model)
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding Error: {e}")
            return []

    def get_response(self, messages: List[Dict]) -> str:
        """
        메시지 리스트를 받아 API를 호출합니다.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM 호출 오류: {str(e)}"