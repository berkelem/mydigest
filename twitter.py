import tweepy
import os
import urllib.request
import json
import random
import time

class TwitterCrawler:

    def __init__(self, n_likes):
        self.api = self.create_api()
        self.username = 'BerkeleyMatthew'
        self.n_likes = n_likes

    @staticmethod
    def create_api():
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        access_token = os.getenv("ACCESS_TOKEN")
        access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)
        try:
            api.verify_credentials()
        except Exception as e:
            if "Failed to establish a new connection" in e.reason:
                time.sleep(60)
                try:
                    api.verify_credentials()
                except Exception:
                    raise e from None
        return api

    @staticmethod
    def create_html_message(title, msg_html):
        html = """<p>
                    <h1>
                      {}
                    </h1>
                  </p>
                  {}""".format(title, msg_html)
        return html

    def load_likes(self):
        likes = tweepy.Cursor(self.api.favorites, id=self.username).items()
        return likes

    def load_tweets(self):
        tweets = tweepy.Cursor(self.api.user_timeline).items()
        return tweets

    def extract_tweet_ids(self, tweet_iterator):
        tweets_id_list = [tweet.id for tweet in tweet_iterator]
        return tweets_id_list

    def pick_n_random(self, tweet_list):
        rand_ints = random.sample(range(len(tweet_list)), self.n_likes)
        tweet_ids = [tweet_list[i] for i in rand_ints]
        return tweet_ids

    def create_html_message_body(self, tweet_ids):

        html_message_body = ""
        for id in tweet_ids:
            tweet_url = "https://twitter.com/twitter/statuses/{}".format(id)
            json_data = urllib.request.urlopen(
                "https://publish.twitter.com/oembed?url={}".format(tweet_url))
            json_data = json.load(json_data)
            html_message_body += json_data["html"]

        return html_message_body

    def get_n_likes(self):
        likes = self.load_likes()
        tweet_id_list = self.extract_tweet_ids(likes)
        selected_ids = self.pick_n_random(tweet_id_list)
        msg_body = self.create_html_message_body(selected_ids)
        html_msg = self.create_html_message("Liked Tweets", msg_body)
        return html_msg

    def get_n_tweets(self):
        tweets = self.load_tweets()
        tweet_id_list = self.extract_tweet_ids(tweets)
        selected_ids = self.pick_n_random(tweet_id_list)
        msg_body = self.create_html_message_body(selected_ids)
        html_msg = self.create_html_message("My Tweets", msg_body)
        return html_msg



