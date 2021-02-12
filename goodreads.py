from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import numpy as np
import random
import re


class WebLoader:

    def __init__(self):
        pass

    @staticmethod
    def init_browser():
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
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
        self.url = 'https://www.goodreads.com/review/list/6157820-matthew?utf8=%E2%9C%93&utf8=%E2%9C%93&order=d&sort=date_read&view=reviews&title=matthew&per_page=750'
        self.browser = self.init_browser()
        self.load_page()
        self.n = n
        self.soup = BeautifulSoup(self.browser.page_source, 'html.parser')

    def load_page(self):
        incomplete = True
        while incomplete:
            try:
                self.browser.get(self.url)
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

    def get_reviews(self):
        book_reviews = self.find_reviews_in_html()
        num_reviews = len(book_reviews)
        rand_ints = random.sample(range(num_reviews), self.n)
        reviews = []
        for i in rand_ints:
            job_elem = book_reviews[i]
            title, review = self.extract_review(job_elem)
            while review == "None":
                j = np.random.randint(0, len(book_reviews))
                if j in rand_ints:
                    continue
                job_elem = book_reviews[j]
                title, review = self.extract_review(job_elem)
            full_book_url = self.get_book_url(job_elem)
            clean_title = title.text.split("\n")[1].strip()
            reviews.append((clean_title, review, full_book_url))
        return reviews

    @staticmethod
    def extract_review(element):
        title = element.find("td", class_="field title")
        review = element.find("span", {"id": lambda l: l and l.startswith('freeTextreview')})
        review = re.sub("<span.*?>", "", str(review))
        review = re.sub("</span>", "", str(review))
        return title, review

    def create_html_message(self, review_tuple):
        title, review, url = review_tuple
        html = """<p><a href="{}">{}</a><br><br>
                     Review: {}<br>       
                  </p> """.format(url, title, review)
        return html
