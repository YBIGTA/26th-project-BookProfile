import json
import random

# Contrastive Loss 학습 데이터
with open("../supcon_books_data.json", "r", encoding="utf-8") as file:
    supcon_data = json.load(file)
    
# Positive & Negative Pair 데이터
positive_pairs = supcon_data["positive_pairs"]

negative_pairs = supcon_data["negative_pairs"]

# RAGAS 평가 데이터 변환
ragas_data = []

for anchor, positive in positive_pairs:
    ragas_data.append({
        "question": anchor,
        "context": positive,
        "answer": f"네, {positive}",
        "relevance": 1.0  # Positive Pair이므로 relevance = 1
    })

for anchor, negative in negative_pairs:
    ragas_data.append({
        "question": anchor,
        "context": negative,
        "answer": "죄송합니다. 해당 질문과 관련된 정보를 찾을 수 없습니다.",
        "relevance": 0.0  # Negative Pair이므로 relevance = 0
    })

# JSON 파일로 저장
with open("ragas_eval_data.json", "w", encoding="utf-8") as f:
    json.dump(ragas_data, f, indent=4, ensure_ascii=False)

print("RAGAS 평가 데이터가 'ragas_eval_data.json' 파일로 저장되었습니다!")

dataset = Dataset.from_list(ragas_data)

# 🔹 RAGAS 평가 실행
results = evaluate(dataset, metrics=[faithfulness, answer_relevance, context_precision])
print("📊 RAGAS 평가 결과:")
print(results)