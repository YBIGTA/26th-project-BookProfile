import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import argparse
from review_crawler import BookInfoCrawler  # review_crawler.py에 BookInfoCrawler 클래스가 정의되어 있다고 가정합니다.
from src.load_data import MongoDBInserter  # mongodb_inserter.py에 MongoDBInserter 클래스가 정의되어 있다고 가정합니다.




def create_parser():
    parser = argparse.ArgumentParser(description="Goodreads 도서 크롤러 실행")
    #parser.add_argument("--output_dir", type=str, required=True, help="출력 디렉토리 경로")
    parser.add_argument("--num_reviews", type=int, default=100, help="수집할 리뷰 수")
    parser.add_argument("--webdriver_path", type=str, default=None, help="Chrome WebDriver 경로 (기본값: None)")
    parser.add_argument("--json_file", type=str, default=r"database\book_links.json", help="도서 링크가 저장된 JSON 파일 경로")
    parser.add_argument("--start_index", type=int, default=199, help="처리할 시작 인덱스 (포함)")
    parser.add_argument("--end_index", type=int, default=201, help="처리할 종료 인덱스 (포함)")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # BookInfoCrawler 인스턴스 생성 (필요한 인자 없이 기본 생성자 사용)
    crawler = BookInfoCrawler(args.num_reviews, args.webdriver_path)
    crawler.start_browser()
    
    # MongoDB 연결용 객체 생성 및 DB 연결
    mongo_inserter = MongoDBInserter()
    mongo_inserter.connect_db()
    
    try:
        # JSON 파일에 저장된 책 링크 중 start_index ~ end_index 범위의 도서를 처리
        crawler.scrap_list(
            json_file=args.json_file,
            start_index=args.start_index,
            end_index=args.end_index,
            mongo_inserter=mongo_inserter
        )
        print("전체 수집 완료")
    except Exception as e:
        print("크롤링 중 오류 발생:", e)
    finally:
        crawler.close_browser()

if __name__ == "__main__":
    main()
