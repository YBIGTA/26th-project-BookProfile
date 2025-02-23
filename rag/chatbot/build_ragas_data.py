import json
import time
from pathlib import Path
import sys

# RAG Chatbot 관련 모듈 로드
from bot.client.lama_cpp_client import LamaCppClient
from bot.conversation.chat_history import ChatHistory
from bot.conversation.conversation_handler import answer_with_context, refine_question
from bot.conversation.ctx_strategy import get_ctx_synthesis_strategy
from bot.memory.vector_database.chroma import Chroma
from bot.model.model_registry import get_model_settings
from helpers.log import get_logger
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision

logger = get_logger(__name__)

# JSON 데이터 로드
file_path = Path(__file__).resolve().parent.parent
with open(f"{file_path}/supcon_books_data.json", "r", encoding="utf-8") as file:
    supcon_data = json.load(file)

positive_pairs = supcon_data["positive_pairs"]
negative_pairs = supcon_data["negative_pairs"]

# RAG 모델 초기화 함수
def load_rag_chatbot():
    root_folder = Path(__file__).resolve().parent.parent
    model_folder = root_folder / "models"
    vector_store_path = root_folder / "vector_store" / "docs_index"

    # 모델 불러오기
    model_name = "llama-3.2"  # 사용하려는 모델 이름 (변경 가능)
    model_settings = get_model_settings(model_name)
    llm = LamaCppClient(model_folder=model_folder, model_settings=model_settings)

    # 채팅 기록 및 컨텍스트 전략 설정
    chat_history = ChatHistory(total_length=2)
    ctx_synthesis_strategy = get_ctx_synthesis_strategy("default", llm=llm)

    # 벡터 데이터베이스 로드
    embedding = Chroma(persist_directory=str(vector_store_path))
    index = Chroma(persist_directory=str(vector_store_path), embedding=embedding)

    return llm, chat_history, ctx_synthesis_strategy, index

# RAG 모델을 사용하여 답변 생성 함수
def get_rag_answer(question, context, llm, chat_history, ctx_synthesis_strategy, index):
    start_time = time.time()
    
    # 질문 리파인먼트
    refined_user_input = refine_question(llm, question, chat_history=chat_history)

    # 문서 검색
    retrieved_contents, _ = index.similarity_search_with_threshold(query=refined_user_input, k=2)

    # 응답 생성
    if retrieved_contents:
        streamer, _ = answer_with_context(llm, ctx_synthesis_strategy, question, chat_history, retrieved_contents)
        full_response = ""
        for token in streamer:
            full_response += llm.parse_token(token)
    else:
        full_response = "죄송합니다. 해당 질문과 관련된 정보를 찾을 수 없습니다."

    took = time.time() - start_time
    logger.info(f"\n--- RAG 응답 생성 완료: {took:.2f} 초 ---")
    return full_response

# RAGAS 평가 데이터 변환
llm, chat_history, ctx_synthesis_strategy, index = load_rag_chatbot()
ragas_data = []

for anchor, positive in positive_pairs:
    generated_answer = get_rag_answer(anchor, positive, llm, chat_history, ctx_synthesis_strategy, index)
    ragas_data.append({
        "question": anchor,
        "context": positive,
        "answer": generated_answer,
        "relevance": 1.0
    })

for anchor, negative in negative_pairs:
    generated_answer = get_rag_answer(anchor, negative, llm, chat_history, ctx_synthesis_strategy, index)
    ragas_data.append({
        "question": anchor,
        "context": negative,
        "answer": generated_answer,
        "relevance": 0.0
    })

# JSON 파일 저장
output_path = file_path / "ragas_eval_data.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ragas_data, f, indent=4, ensure_ascii=False)

print(f"✅ RAGAS 평가 데이터가 '{output_path}' 파일로 저장되었습니다!")

# 🔹 RAGAS 평가 실행
dataset = Dataset.from_list(ragas_data)
results = evaluate(dataset, metrics=[faithfulness, answer_relevance, context_precision])

print("📊 RAGAS 평가 결과:")
print(results)
