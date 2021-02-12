import goodreads
import twitter
import sendemail

if __name__ == "__main__":

    gdr_reader = goodreads.Goodreads(1)
    twttr_scraper = twitter.TwitterCrawler(3)
    email = sendemail.DigestEmail()

    reviews = gdr_reader.get_reviews()
    html_message = """"""
    for review in reviews:
        html_message += gdr_reader.create_html_message(review)

    tweet_likes_html = twttr_scraper.get_n_likes()
    html_message += tweet_likes_html

    final_html_message = email.compile_html_text(html_message)

    email.yag_send(final_html_message)
