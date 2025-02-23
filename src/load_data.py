from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os
import re
from datetime import datetime
import sys

class MongoDBInserter:
    def __init__(self):
        """
        클래스 초기화 메서드.
        
        이 메서드는 다음과 같은 작업을 수행합니다:
        - .env 파일에서 환경 변수를 로드합니다.
        - 'MONGO_URI' 환경 변수에서 MongoDB 연결 URI를 가져오고, 'json_file_path' 환경 변수에서 JSON 파일 경로를 가져옵니다.
        - 필수 환경 변수가 설정되어 있지 않으면 ValueError를 발생시킵니다.
        - MongoDB 클라이언트, 데이터베이스, 그리고 컬렉션(books와 reviews)을 초기값 None으로 설정합니다.
        
        Raises:
            ValueError: 'MONGO_URI' 또는 'json_file_path' 환경 변수가 설정되지 않은 경우.
        """
        load_dotenv()

        self.connection_URI = os.getenv("MONGO_URI")
        self.json_file_path = os.getenv("json_file_path")
        
        if self.connection_URI is None:
            raise ValueError("환경 변수 'MONGO_URI' 설정 필요")
        if self.json_file_path is None:
            raise ValueError("환경 변수 'json_file_path' 설정 필요")
        
        self.client = None
        self.db = None
        self.books_collection = None
        self.reviews_collection = None

    def connect_db(self):
        """
        MongoDB에 연결하고 'crawling' 데이터베이스의 컬렉션들을 초기화합니다.

        이 메서드는 다음 작업을 수행합니다:
        - 환경 변수로부터 설정된 MongoDB URI를 사용하여 클라이언트를 생성합니다.
        - 'crawling' 데이터베이스에 연결합니다.
        - 'books'와 'reviews' 컬렉션을 초기화합니다.
        
        연결에 성공하면 "MongoDB 연결 성공" 메시지를 출력하며,
        실패할 경우 예외 메시지를 출력하고 프로그램을 종료합니다.
        """
        try:
            self.client = MongoClient(self.connection_URI)
            self.db = self.client.get_database("crawling")
            self.books_collection = self.db.get_collection("books")
            self.reviews_collection = self.db.get_collection("reviews")
            print("MongoDB 연결 성공")
        except Exception as e:
            print("MongoDB 연결 실패:", e)
            sys.exit(1)

    def load_books_data(self):
        """
        JSON 파일에서 책 데이터를 읽어와 반환합니다.

        이 메서드는 다음과 같은 작업을 수행합니다:
        - 환경 변수로 지정된 JSON 파일 경로에서 파일을 읽어옵니다.
        - 파일의 전체 내용을 문자열로 가져온 후, JSONDecoder의 raw_decode() 메서드를 이용해
            연속된 JSON 객체({ } { } 형식)를 개별적으로 파싱합니다.
        - 파싱한 각 JSON 객체를 리스트에 추가하여 최종적으로 책 데이터 리스트를 반환합니다.

        Returns:
            list: JSON 파일에서 읽어온 책 데이터의 리스트.

        Raises:
            SystemExit: 파일 읽기 또는 JSON 디코딩 중 오류가 발생한 경우, 예외 메시지를 출력하고 프로그램을 종료합니다.
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as jsonfile:
                content = jsonfile.read()

            books_data = []
            decoder = json.JSONDecoder()
            pos = 0
            length = len(content)

            while pos < length:
                # 현재 위치의 공백 문자 건너뛰기
                m = re.compile(r'\s*').match(content, pos)
                if m:
                    pos = m.end()
                if pos >= length:
                    break
                try:
                    obj, pos = decoder.raw_decode(content, pos)
                    books_data.append(obj)
                except json.JSONDecodeError as e:
                    print("JSON 디코드 오류:", e)
                    break

            print("JSON 파일 읽기 성공")
            return books_data
        except Exception as e:
            print("JSON 파일 읽기 실패:", e)
            sys.exit(1)

    def book_exists(self, book_name):
        """
        주어진 책 제목이 books 컬렉션에 이미 존재하는지 확인합니다.

        Args:
            book_name (str): 확인할 책의 제목.

        Returns:
            bool: 책이 존재하면 True, 그렇지 않으면 False.
        """
        query = {"book_name": book_name}
        book = self.books_collection.find_one(query)
        return book is not None

    def insert_book(self, book):
        """
        책 데이터를 books 컬렉션에 삽입하고, 삽입된 문서의 _id를 반환합니다.

        Args:
            book (dict): 삽입할 책 데이터(딕셔너리 형태).

        Returns:
            ObjectId: 삽입된 책 문서의 _id를 반환합니다.
            삽입 실패 시 None을 반환합니다.
        """
        try:
            result = self.books_collection.insert_one(book)
            book_id = result.inserted_id
            print(f"책 삽입 성공 - book_id: {book_id}")
            return book_id
        except Exception as e:
            print("책 삽입 실패:", e)
            return None

    def preprocess_reviews(self, reviews, book_id):
        """
        각 리뷰에 대해 날짜와 평점 전처리 작업을 수행하고, book_id를 추가합니다.

        Args:
            reviews (list): 전처리할 리뷰들의 리스트.
            book_id: 각 리뷰에 추가할 책의 _id.

        Returns:
            list: 전처리가 완료된 리뷰들의 리스트.
        """
        processed_reviews = []
        for review in reviews:
            try:
                # 날짜 전처리: 예) "June 10, 2023" -> "2023-06-10"
                date_obj = datetime.strptime(review["date"], "%B %d, %Y")
                review["date"] = date_obj.strftime("%Y-%m-%d")
            except Exception as e:
                print("리뷰 날짜 전처리 실패:", e)
                review["date"] = None

            # 평점 전처리: 숫자만 추출, 없으면 None
            match = re.search(r'(\d+)', review.get("rating", ""))
            if match:
                review["rating"] = int(match.group(1))
            else:
                review["rating"] = None

            review["book_id"] = book_id
            processed_reviews.append(review)
        return processed_reviews

    def insert_reviews(self, reviews):
        """
        리뷰 데이터를 reviews 컬렉션에 삽입합니다.

        이 메서드는 다음과 같은 작업을 수행합니다:
        - reviews 리스트가 비어있지 않은 경우, insert_many() 메서드를 사용하여 리뷰 데이터를 MongoDB의 reviews 컬렉션에 삽입합니다.
        - 삽입이 성공하면 삽입된 리뷰 건수를 출력합니다.
        - 삽입 중 오류가 발생하면 오류 메시지를 출력합니다.

        Args:
            reviews (list): 삽입할 리뷰 데이터 리스트. 각 리뷰는 딕셔너리 형식입니다.
        """
        if reviews:
            try:
                result = self.reviews_collection.insert_many(reviews)
                print(f"리뷰 {len(result.inserted_ids)}건 삽입 성공")
            except Exception as e:
                print("리뷰 삽입 실패:", e)

    def run(self):
        """
        전체 데이터 삽입 과정을 순차적으로 실행합니다.

        이 메서드는 다음과 같은 작업을 수행합니다:
            1. MongoDB에 연결합니다.
            2. JSON 파일에서 책 데이터를 읽어옵니다.
            3. 각 책 데이터에 대해:
                - 'book_name' 키가 없는 경우 해당 데이터를 건너뜁니다.
                - 이미 존재하는 책이면 건너뜁니다.
                - 'reviews' 키가 있으면 해당 값을 추출하고, 책 데이터에서 제거합니다.
                - 책 데이터를 삽입하여 삽입된 문서의 _id를 가져옵니다.
                - 추출한 리뷰 데이터를 전처리한 후 reviews 컬렉션에 삽입합니다.
            4. 모든 데이터 삽입 작업이 완료되면 완료 메시지를 출력합니다.
        """
        self.connect_db()
        books_data = self.load_books_data()

        for book in books_data:
            # 중복 체크
            book_name = book.get("book_name")
            if not book_name:
                print("book_name 키가 없는 데이터 건너뜀")
                continue

            if self.book_exists(book_name):
                print(f"책 '{book_name}'은 이미 존재합니다. 건너뜁니다.")
                continue

            # reviews 추출
            reviews = book.pop("reviews", [])

            # 책 삽입
            book_id = self.insert_book(book)
            if book_id is None:
                continue

            # 리뷰 전처리 및 삽입
            processed_reviews = self.preprocess_reviews(reviews, book_id)
            self.insert_reviews(processed_reviews)
        
        print("데이터 삽입 완료")

    def run_di2(self, book):
        """
        전체 데이터 삽입 과정을 순차적으로 실행합니다.

        이 메서드는 다음과 같은 작업을 수행합니다:
            1. MongoDB에 연결합니다.
            2. JSON 파일에서 책 데이터를 읽어옵니다.
            3. 각 책 데이터에 대해:
                - 'book_name' 키가 없는 경우 해당 데이터를 건너뜁니다.
                - 이미 존재하는 책이면 건너뜁니다.
                - 'reviews' 키가 있으면 해당 값을 추출하고, 책 데이터에서 제거합니다.
                - 책 데이터를 삽입하여 삽입된 문서의 _id를 가져옵니다.
                - 추출한 리뷰 데이터를 전처리한 후 reviews 컬렉션에 삽입합니다.
            4. 모든 데이터 삽입 작업이 완료되면 완료 메시지를 출력합니다.
        """
        
        self.connect_db()
        print("run_di 실행")
        
        
        # 중복 체크
        book_name = book.get("book_name")
        if not book_name:
            print("book_name 키가 없는 데이터 건너뜀")
            return


        if self.book_exists(book_name):
            print(f"책 '{book_name}'은 이미 존재합니다. 삭제 후 삽입.")
            self.collection.delete_one({"book_name": book_name})
            


        # reviews 추출
        reviews = book.pop("reviews", [])

        # 책 삽입
        book_id = self.insert_book(book)
        if book_id is not None:


            # 리뷰 전처리 및 삽입
            processed_reviews = self.preprocess_reviews(reviews, book_id)
            self.insert_reviews(processed_reviews)
            
            print("데이터 삽입 완료")


def main():
    """
    MongoDBInserter 인스턴스를 생성하고, 전체 데이터 삽입 과정을 실행하는 메인 함수입니다.
    """
    inserter = MongoDBInserter()
    inserter.run_di2()

if __name__ == "__main__":
    main()