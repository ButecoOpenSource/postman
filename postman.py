import logging
from os import getenv

# global configuration
logging.basicConfig(level=logging.DEBUG)

# RSS
ENV_RSS_SOURCE = "RSS_SOURCE"
RSS_SOURCE = ""

# Twitter
ENV_TWITTER_ACCESS_TOKEN = "TWITTER_ACCESS_TOKEN"
ENV_TWITTER_ACCESS_TOKEN_SECRET = "TWITTER_ACCESS_TOKEN_SECRET"
ENV_TWITTER_CONSUMER_KEY = "TWITTER_CONSUMER_KEY"
ENV_TWITTER_CONSUMER_SECRET = "TWITTER_CONSUMER_SECRET"

TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""

# Faceboo""
ENV_FACEBOOK_PAGE_ID = "FACEBOOK_PAGE_ID";
ENV_FACEBOOK_TOKEN = "FACEBOOK_TOKEN"

FACEBOOK_PAGE_ID = ""
FACEBOOK_TOKEN = ""

# Collect articles
from xml.dom import minidom
import requests


def collect_articles(feed_url):
    res = requests.get(feed_url)
    data = res.text
    feed = minidom.parseString(data)
    articles = []
    for entry in feed.getElementsByTagName("entry"):
        _id = entry.getElementsByTagName("id")[0].firstChild.nodeValue,
        logging.info("Adding {}".format(_id))
        articles.append({
            "id": _id,
            "title": entry.getElementsByTagName("title")[0].firstChild.nodeValue,
            "link": entry.getElementsByTagName("link")[0].attributes["href"].value,
            "published": entry.getElementsByTagName("published")[0].firstChild.nodeValue,
            "updated": entry.getElementsByTagName("updated")[0].firstChild.nodeValue,
            "author_name": entry.getElementsByTagName("author")[0].getElementsByTagName("name")[0].firstChild.nodeValue,
            "author_email": "" if len(entry.getElementsByTagName("author")[0].getElementsByTagName("email")) == 0 else
            entry.getElementsByTagName("author")[0].getElementsByTagName("email")[0].firstChild.nodeValue,
            "categories": [f.attributes["term"].nodeValue for f in entry.getElementsByTagName("category")],
            "summary": entry.getElementsByTagName("summary")[0].firstChild.nodeValue,
        })
    logging.info("Got {} articles".format(len(articles)))
    return articles


# Post to twitter
from twitter import *


def post_article_to_twitter(article):
    tweet = "{} {} {}".format(article["title"], article["link"],
                              " ".join(["#{}".format(f) for f in article["categories"]]))
    t = Twitter(
        auth=OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET))
    logging.info("Tweeting: {}".format(tweet))
    t.statuses.update(status=tweet)


# Post to Facebook
from facebook import *


def post_article_to_facebook(article):
    post = "{} {}".format(article["title"], " ".join(["#{}".format(f) for f in article["categories"]]))
    graph = GraphAPI(access_token=FACEBOOK_TOKEN, version="2.12")
    logging.info("Posting {} to Facebook Page".format(post))
    graph.put_object(
        parent_object=FACEBOOK_PAGE_ID,
        connection_name="feed",
        message=post,
        link=article["link"])


def load_env():
    error_messages = []

    global RSS_SOURCE
    RSS_SOURCE = getenv(ENV_RSS_SOURCE, "")
    if RSS_SOURCE == "":
        error_messages.append("RSS_SOURCE is empty")

    global TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN = getenv(ENV_TWITTER_ACCESS_TOKEN, "")
    if TWITTER_ACCESS_TOKEN == "":
        error_messages.append("TWITTER_ACCESS_TOKEN is empty")

    global TWITTER_ACCESS_TOKEN_SECRET
    TWITTER_ACCESS_TOKEN_SECRET = getenv(ENV_TWITTER_ACCESS_TOKEN_SECRET, "")
    if TWITTER_ACCESS_TOKEN_SECRET == "":
        error_messages.append("TWITTER_ACCESS_TOKEN_SECRET is empty")

    global TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_KEY = getenv(ENV_TWITTER_CONSUMER_KEY, "")
    if TWITTER_CONSUMER_KEY == "":
        error_messages.append("TWITTER_CONSUMER_KEY is empty")

    global TWITTER_CONSUMER_SECRET
    TWITTER_CONSUMER_SECRET = getenv(ENV_TWITTER_CONSUMER_SECRET, "")
    if TWITTER_CONSUMER_SECRET == "":
        error_messages.append("TWITTER_CONSUMER_SECRET is empty")

    global FACEBOOK_PAGE_ID
    FACEBOOK_PAGE_ID = getenv(ENV_FACEBOOK_PAGE_ID, "")
    if FACEBOOK_PAGE_ID == "":
        error_messages.append("FACEBOOK_PAGE_ID is empty")

    global FACEBOOK_TOKEN
    FACEBOOK_TOKEN = getenv(ENV_FACEBOOK_TOKEN, "")
    if FACEBOOK_TOKEN == "":
        error_messages.append("FACEBOOK_TOKEN is empty")

    if len(error_messages):
        logging.error("\n".join(error_messages))
        exit(1)


if __name__ == "__main__":
    load_env()
    articles = collect_articles(RSS_SOURCE)
    for article in articles:
        logging.info("Sharing article '{}'".format(article["title"]))
        post_article_to_twitter(article=article)
        post_article_to_facebook(article=article)
