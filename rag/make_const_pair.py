import json
import itertools
from collections import defaultdict

with open("remnent.json", "r", encoding="utf-8") as file:
    books_data = json.load(file)
supcon_data = defaultdict(lambda: {"positive_pairs": [], "negative_pairs": []})

# rating을 숫자로 변환하는 함수
def extract_rating(rating_str):
    return int(rating_str.split()[1])  # "Rating 4 out of 5" -> 4

# 각 책 별로 Positive/Negative Pairs 생성
for book in books_data:
    book_name = book["book_name"]
    reviews = book["reviews"]

    # 모든 리뷰 조합 비교
    for review1, review2 in itertools.combinations(reviews, 2):
        rating1 = extract_rating(review1["rating"])
        rating2 = extract_rating(review2["rating"])

        # Positive Pair (같은 책 & rating 차이 1 이내)
        if abs(rating1 - rating2) <= 1:
            supcon_data["positive_pairs"].append((review1['review'], review2['review']))

        # Negative Pair (같은 책 & rating 차이 3 이상)
        elif abs(rating1 - rating2) >= 3:
            supcon_data["negative_pairs"].append((review1['review'], review2['review']))

# 결과 확인
for book_name, pairs in supcon_data.items():
    print(f"📘 [{book_name}] SupCon 데이터 생성 완료!")
    print(f"✅ Positive Pairs: {len(pairs['positive_pairs'])}")
    print(f"❌ Negative Pairs: {len(pairs['negative_pairs'])}")

# JSON 파일로 저장 (필요한 경우)
with open("supcon_books_data.json", "w", encoding="utf-8") as f:
    json.dump(supcon_data, f, indent=4, ensure_ascii=False)