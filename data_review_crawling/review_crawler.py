from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import os
import json
from src.load_data import MongoDBInserter
from typing import Dict, Optional, Any
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class BookInfoCrawler:
    def __init__(self,  num_reviews: int, webdriver_path: Optional[str] = None ):
        """
        도서 상세 정보와 리뷰를 수집하는 크롤러 초기화

        Args:
            output_dir (str): 결과 파일을 저장할 디렉토리
            webdriver_path (str): ChromeDriver 실행 파일 경로
            num_reviews (int): 한 책당 수집할 리뷰의 개수
        """
        #self.output_dir = output_dir
        self.webdriver_path = webdriver_path
        #self.num_books = num_books
        self.num_reviews = num_reviews
        self.driver = None

        self.book_info: Dict[str, Any] = {}
        self.output = None

        # 로그인 오버레이 닫기 버튼 CSS 셀렉터
        self.login_overlay_dismiss_selector = "body > div.Overlay.Overlay--floating > div > div.Overlay__header > div > div > button"
        
        # 언어 필터 관련 XPath 정보
        self.launguage_filter = {
            "filter": "//*[@id='ReviewsSection']/div[5]/div[2]/div[1]/div[2]/div/button",
            "en_label": "/html/body/div[3]/div/div[2]/span/div/div[6]/div[2]/label",
            "apply": "/html/body/div[3]/div/div[3]/div[2]/button",
            "text": "/html/body/div[3]/div/div[2]/span/div/div[6]/div[2]/label/text()"
        }


        # scrap_book 에서 사용되는 XPath들
        self.book_detail_path = '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/div/button'
        self.xpath = {
            'book_name': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[1]/div[1]/h1',
            'book_image': '//*[@id="__next"]/div[2]/main/div[1]/div[1]/div/div[1]/div/div/div/div/div/div/img',
            'author': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[1]/h3/div/span[1]/a/span',
            'total_star': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[2]/a/div[1]/div',
            'published': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[1]/span/div/p[2]',
            'description': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[1]/div/div/span',
            'ISBN': '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[6]/div/span[2]/div[1]/span/div/dl/div[3]/dd/div/div[1]'
        }

        # scrap_reviews 관련 XPath들
        self.view_more_reviews_button_xpath = '//*[@id="ReviewsSection"]/div[6]/div[4]/a'
        self.filter_button_xpath = '//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[4]/div[1]/div[2]/div/button'
        self.english_label_xpath = '/html/body/div[3]/div/div[2]/span/div/div[6]/div[3]/label/span'
        self.apply_button_xpath = '/html/body/div[3]/div/div[3]/div[2]/button'
        self.show_more_button_xpath = "//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[5]/div/button"
        self.review_xpaths = {
            "reviewer": "//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[3]/div[INDEX]/article/div/div/section[2]/span[1]/div/a",
            "date":     "//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[3]/div[INDEX]/article/section/section[1]/span/a",
            "rating":   "//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[3]/div[INDEX]/article/section/section[1]/div/span",
            "review":   "//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[3]/div[INDEX]/article/section/section[2]/section/div/div[1]/span"
        }

    def start_browser(self, webdriver_path: Optional[str] = None) -> webdriver.Chrome:
        """
        Selenium WebDriver(Chrome) 객체를 생성하여 브라우저를 시작합니다.
        시스템 기본 path에 webdriver가 있을 경우 webdriver_path를 None으로 두면 됩니다.
        options 에서 필요에 따라 option을 추가하세요.
        
        Args:
            webdriver_path (Optional[str]): 크롬드라이버 경로. 기본값은 None이며,
                                            시스템 환경 변수 설정을 사용할 경우 None으로 두면 됩니다.
        
        Returns:
            webdriver.Chrome: 생성된 Chrome WebDriver 객체.
        """
        # Chrome WebDriver 옵션 설정
        options = Options()


        # Headless 모드: 브라우저 창을 띄우지 않고 백그라운드에서 실행합니다.
        # options.add_argument("--headless")

        # --no-sandbox: 샌드박스 모드를 비활성화합니다.
        # 일부 리눅스 환경이나 컨테이너 환경에서 권한 문제를 피하기 위해 사용합니다.
        options.add_argument("--no-sandbox")

        # --disable-dev-shm-usage: /dev/shm(공유 메모리) 사용을 비활성화합니다.
        # Docker와 같이 /dev/shm 용량이 제한된 환경에서 메모리 부족 문제를 방지하기 위해 사용됩니다.
        options.add_argument("--disable-dev-shm-usage")

        # --disable-blink-features=AutomationControlled: 자동화 제어 플래그를 비활성화하여
        # 웹사이트에서 Selenium을 통한 자동화 제어 여부를 감지하지 못하도록 합니다.
        options.add_argument("--disable-blink-features=AutomationControlled")

        # user-agent 설정: 서버에 전달되는 브라우저 식별 문자열(User Agent)을 변경합니다.
        # 실제 사용자 브라우저처럼 보이게 하여, 자동화 스크립트임을 감추기 위해 사용합니다.
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        # --lang=ko_KR: 브라우저의 기본 언어를 한국어로 설정합니다.
        # 웹사이트가 언어 설정에 따라 다르게 동작할 경우, 한국어 환경으로 테스트할 수 있습니다.
        options.add_argument("--lang=ko_KR")

        # --charset=utf-8: 문자 인코딩을 UTF-8로 설정하려는 시도입니다.
        # (참고: 이 옵션은 크롬에서 공식적으로 지원하지 않을 수 있으므로, 실제 효과는 미미할 수 있습니다.)
        options.add_argument("--charset=utf-8")
        
        # WebDriver 객체 생성
        if webdriver_path:
            service = Service(webdriver_path)
        else:
            service = Service()  # 시스템 환경 변수에 설정된 경로를 사용
        
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def apply_language_filter(self):
        """
        언어 필터 버튼을 클릭하여 'English' 옵션을 적용합니다.
        """
        try:
            filter_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.launguage_filter['filter']))
            )
            filter_button.click()
            time.sleep(1)
            en_label = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[3]/div/div[2]/span/div/div[6]/div[label[starts-with(normalize-space(text()), 'English')]]/label")
                )
            )
            en_label.click()
            time.sleep(1)
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.launguage_filter['apply']))
            )
            apply_button.click()
            print("언어 필터 적용 완료")
        except Exception as e:
            print("언어 필터 적용 중 오류 발생:", e)

    def check_and_dismiss_overlay(self, timeout=5):
        """
        로그인 오버레이가 있으면 해제합니다.
        """
        end_time = time.time() + timeout
        dismissed = False
        while time.time() < end_time:
            try:
                dismiss_button = self.driver.find_element(By.CSS_SELECTOR, self.login_overlay_dismiss_selector)
                if dismiss_button.is_displayed() and dismiss_button.is_enabled():
                    dismiss_button.click()
                    print("로그인 오버레이가 해제되었습니다.")
                    dismissed = True
                    break
            except Exception:
                break
            time.sleep(0.5)
        return dismissed

    def scrap_book(self):
        """
        도서 상세 페이지에서 책 정보를 추출한 후,
        리뷰 페이지로 이동하여 리뷰를 수집합니다.
        """
        try:
            book_detail_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.book_detail_path))
            )
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.Overlay.Overlay--floating"))
            )
            book_detail_button.click()
            time.sleep(2)
        except Exception as e:
            print("book details 버튼 클릭 중 오류 발생:", e)
        
        self.apply_language_filter()

        # 책 정보 추출
        self.book_info = {}
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.xpath['book_name']))
            )
        except Exception as e:
            print("책 정보 로딩 중 오류 발생:", e)
            
        for key, xpath_val in self.xpath.items():
            try:
                element = self.driver.find_element(By.XPATH, xpath_val)
                if key == 'book_image':
                    self.book_info[key] = element.get_attribute("src")
                else:
                    self.book_info[key] = element.text.strip()
            except Exception as e:
                print(f"{key} 정보 추출 중 오류 발생: {e}")
                self.book_info[key] = None

        # 장르 정보 추출
        genres = []
        index = 2
        while True:
            try:
                genre_xpath = f'//*[@id="__next"]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div[5]/ul/span[1]/span[{index}]/a/span'
                genre_element = self.driver.find_element(By.XPATH, genre_xpath)
                genres.append(genre_element.text.strip())
                index += 1
            except Exception:
                break
        self.book_info['genre'] = genres

        # 오버레이 해제 시도
        self.check_and_dismiss_overlay(timeout=5)
        
        # 리뷰 페이지로 이동
        try:
            view_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.view_more_reviews_button_xpath))
            )
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.Overlay.Overlay--floating"))
            )
            view_more_button.click()
            time.sleep(2)
        except Exception as e:
            print("리뷰 페이지로 이동하는 'view more reviews' 버튼 클릭 중 오류 발생:", e)
            self.book_info['reviews'] = []
            return self.book_info
        
        # 리뷰 수집
        reviews = self.scrap_reviews(target_review_count=self.num_reviews)
        self.book_info['reviews'] = reviews
        
        return self.book_info

    def scrap_reviews(self, target_review_count=100):
        """
        리뷰 컨테이너에서 리뷰 정보를 추출합니다.
        추가 리뷰 로딩이 필요하면 "show more reviews" 버튼을 클릭합니다.
        """
        reviews = []
        current_index = 1
        max_failures = 3
        consecutive_failures = 0

        while len(reviews) < target_review_count:
            container_xpath = f"//*[@id='__next']/div[2]/main/div[1]/div[2]/div[5]/div[3]/div[{current_index}]"
            try:
                self.driver.find_element(By.XPATH, container_xpath)
                consecutive_failures = 0
            except Exception:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    try:
                        show_more_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, self.show_more_button_xpath))
                        )
                        show_more_button.click()
                        time.sleep(2)
                        consecutive_failures = 0
                    except Exception as e:
                        print("show more reviews 버튼 클릭 실패:", e)
                        break
                current_index += 1
                continue

            review_data = {}
            extraction_success = True
            for key, xpath_template in self.review_xpaths.items():
                xpath = xpath_template.replace("INDEX", str(current_index))
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if key == "rating":
                        review_data[key] = element.get_attribute("aria-label").strip()
                    else:
                        review_data[key] = element.text.strip()
                except Exception:
                    extraction_success = False
                    break
            if extraction_success and review_data.get("review", ""):
                reviews.append(review_data)
                consecutive_failures = 0
            else:
                consecutive_failures += 1

            if len(reviews) >= target_review_count:
                break

            current_index += 1

            if consecutive_failures >= max_failures:
                try:
                    show_more_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, self.show_more_button_xpath))
                    )
                    show_more_button.click()
                    time.sleep(2)
                    consecutive_failures = 0
                except Exception as e:
                    print("더 이상 리뷰 로딩 불가 또는 show more reviews 클릭 중 오류 발생:", e)
                    break

        if consecutive_failures >= max_failures:
            print("연속 리뷰 추출 실패 횟수 초과, 리뷰 수집 종료")
        return reviews

    def scrap_list(self, json_file: str, start_index: int, end_index: int, mongo_inserter):
        """
        JSON 파일에 저장된 책 링크 데이터를 이용하여 지정한 인덱스 범위 내의 책을 처리합니다.
        
        JSON 파일 구조 예시:
            {
                "1": ["영문 책 제목", "https://www.goodreads.com/book/show/12345-book-name"],
                "2": ["영문 책 제목", "https://www.goodreads.com/book/show/67890-book-name"],
                ...
            }
        
        Args:
            json_file (str): 책 링크 데이터가 저장된 JSON 파일 경로.
            start_index (int): 처리 시작 인덱스 (포함).
            end_index (int): 처리 종료 인덱스 (포함).
            mongo_inserter: DB 저장을 위한 객체 (self.save_book_to_db에 전달).
        """
        # JSON 파일에서 책 링크 데이터를 로드합니다.
        with open(json_file, "r", encoding="utf-8") as f:
            book_data_dict = json.load(f)
        
        # 지정한 인덱스 범위 내의 각 책에 대해 처리합니다.
        for idx in range(start_index, end_index + 1):
            key = str(idx)
            if key in book_data_dict:
                # JSON 데이터는 [책 제목, url] 형태로 저장되어 있다고 가정합니다.
                book_title, url = book_data_dict[key]
                print(f"책 링크 처리 (Index {idx}): {url}")
                
                # URL 접속
                self.driver.get(url)
                time.sleep(3)
                
                # 오버레이가 있다면 해제
                self.check_and_dismiss_overlay(timeout=5)
                
                # 책 상세 정보를 스크랩합니다.
                book_details = self.scrap_book()
                
                # 스크랩한 데이터를 DB에 저장합니다.
                mongo_inserter.run_di(book_details)
            else:
                print(f"Index {idx} not found in JSON data.")


    def close_browser(self):
        """브라우저를 종료합니다."""
        if self.driver:
            self.driver.quit()
