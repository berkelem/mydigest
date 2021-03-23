import goodreads
import twitter
import sendemail

if __name__ == "__main__":

    gdr_reader = goodreads.Goodreads(1)
    twttr_scraper = twitter.TwitterCrawler(3)
    email = sendemail.DigestEmail()

    my_reviews, my_name = gdr_reader.get_my_reviews()
    other_reviews, other_name = gdr_reader.get_other_reviews()
    html_message = """"""
    for review in my_reviews:
        header = "Review by {}".format(my_name)
        html_message += gdr_reader.create_html_message(review, header=header)

    for review in other_reviews:
        header = "Review by {}".format(other_name)
        html_message += gdr_reader.create_html_message(review, header=header)

    tweet_likes_html = twttr_scraper.get_n_likes()
    html_message += tweet_likes_html

    tweets_html = twttr_scraper.get_n_tweets()
    html_message += tweets_html

    final_html_message = email.compile_html_text(html_message)

    email.yag_send(final_html_message)
