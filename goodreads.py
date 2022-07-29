from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import numpy as np
import random
import re
import chromedriver_autoinstaller


class WebLoader:

    def __init__(self):
        pass

    @staticmethod
    def init_browser():
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        chromedriver_autoinstaller.install()
        browser = webdriver.Chrome(options=options)
        return browser

    @staticmethod
    def scroll_down(driver):
        """A method for scrolling the page. From https://stackoverflow.com/a/48851166/4844311"""

        # Get scroll height.
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(3)

            # Calculate new scroll height and compare with last scroll height.
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height


class Goodreads(WebLoader):

    def __init__(self, n):
        super().__init__()
        # self.url = 'https://www.goodreads.com/review/list/6157820-matthew?utf8=%E2%9C%93&utf8=%E2%9C%93&order=d&sort=date_read&view=reviews&title=matthew&per_page=750'
        self.browser = self.init_browser()
        self.n = n
        self.soup = None
        self.other_reviewers = ["1923320-jessica", "19090274-zbigniew-zdziarski", "6100646-brian-clegg", "922495-patrick", "1713956-manny-rayner"]


        #
        # "https://www.goodreads.com/review/list/1923320-jessica?utf8=%E2%9C%93&order=d&sort=review&view=reviews&title=jessica&per_page=infinite"
        # "https://www.goodreads.com/review/list/19090274-zbigniew-zdziarski?utf8=%E2%9C%93&order=d&sort=review&view=reviews&title=zbigniew-zdziarski&per_page=infinite"
        # "https://www.goodreads.com/review/list/6100646-brian-clegg?utf8=%E2%9C%93&title=brian-clegg&per_page=infinite"

    def construct_url(self, user_id):
        user_num, user_name = user_id.split("-", 1)
        url = "https://www.goodreads.com/review/list/{}?utf8=%E2%9C%93&title={}&per_page=infinite".format(user_id, user_name)
        return url, user_name

    def load_page(self, url):
        incomplete = True
        while incomplete:
            try:
                self.browser.get(url)
                incomplete = False
            except WebDriverException:
                continue

        time.sleep(1)
        self.scroll_down(self.browser)

    def find_reviews_in_html(self):
        results = self.soup.find(id='books')
        book_reviews = results.find_all('tr', class_='bookalike review')
        return book_reviews

    def get_book_url(self, job_elem):
        links = job_elem.findChildren("td", class_="field title", recursive=False)
        book_url = links[0].findChildren("a", href=True)[0]["href"]
        full_book_url = "https://www.goodreads.com{}".format(book_url)
        return full_book_url

    def format_name(self, name):
        clean_name = name.replace("-", " ").title()
        return clean_name

    def get_my_reviews(self):
        url, name = self.construct_url("6157820-matthew")
        clean_name = self.format_name(name)
        reviews = self.get_reviews(url)
        return reviews, clean_name

    def get_other_reviews(self):
        randidx = random.randint(0, len(self.other_reviewers) - 1)
        url, name = self.construct_url(self.other_reviewers[randidx])
        clean_name = self.format_name(name)
        reviews = self.get_reviews(url)
        return reviews, clean_name

    def get_reviews(self, url):
        self.load_page(url)
        self.soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        book_reviews = self.find_reviews_in_html()
        num_reviews = len(book_reviews)
        rand_ints = random.sample(range(num_reviews), self.n)
        reviews = []
        for i in rand_ints:
            job_elem = book_reviews[i]
            title, author, review = self.extract_review(job_elem)
            while review == "None":
                j = np.random.randint(0, len(book_reviews))
                if j in rand_ints:
                    continue
                job_elem = book_reviews[j]
                title, author, review = self.extract_review(job_elem)
            full_book_url = self.get_book_url(job_elem)
            clean_title = title.text.split("\n")[1].strip()
            clean_author = " ".join(author.text.split("author ")[1].strip().split(", ")[::-1])
            reviews.append((clean_title, clean_author, review, full_book_url))
        return reviews

    @staticmethod
    def extract_review(element):
        title = element.find("td", class_="field title")
        author = element.find("td", class_="field author")
        review = element.find("span", {"id": lambda l: l and l.startswith('freeTextreview')})
        review = re.sub("<span.*?>", "", str(review))
        review = re.sub("</span>", "", str(review))
        return title, author, review

    def create_html_message(self, review_tuple, header=None):
        title, author, review, url = review_tuple
        html = """<p>
                    <h1>
                      {}
                    </h1>
                    <a href="{}">{}</a> by {}
                    <br><br>
                    {}<br>       
                  </p> """.format(header, url, title, author, review)
        return html
