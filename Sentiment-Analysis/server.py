"""
A server that responds with two pages, one showing the most recent
100 tweets for given user and the other showing the followers
of a given user (sorted by the number of followers those users have).

For authentication purposes, the server takes a commandline argument
that indicates the file containing Twitter data in a CSV file format:

    consumer_key, consumer_secret, access_token, access_token_secret

For example, I pass in my secrets via file name:

    /Users/parrt/Dropbox/licenses/twitter.csv

Please keep in mind the limits imposed by the twitter API:

    https://dev.twitter.com/rest/public/rate-limits

For example, you can only do 15 follower list fetches per
15 minute window, but you can do 900 user timeline fetches.
"""
import sys
from flask import Flask, render_template
from tweetie import *
from colour import Color

from numpy import median

app = Flask(__name__)


def add_color(tweets):
    """
    Given a list of tweets, one dictionary per tweet, add
    a "color" key to each tweets dictionary with a value
    containing a color graded from red to green. Pure red
    would be for -1.0 sentiment score and pure green would be for
    sentiment score 1.0.

    Use colour.Color to get 100 color values in the range
    from red to green. Then convert the sentiment score from -1..1
    to an index from 0..100. That index gives you the color increment
    from the 100 gradients.

    This function modifies the dictionary of each tweet. It lives in
    the server script because it has to do with display not collecting
    tweets.
    """
    colors = list(Color("red").range_to(Color("green"), 100))
    for t in tweets:
        score = t['score']
        c_score = (score + 1)*50
        t['color'] = str(colors[int(c_score)])

@app.route("/<name>")
def tweets(name):
    "Display the tweets for a screen name color-coded by sentiment score"

    fetched = fetch_tweets(api, name)
    add_color(fetched['tweets'])

    scores = [t['score'] for t in fetched['tweets']]
    m_score = median(scores)

    for tweet in fetched['tweets']:
        href = 'https://twitter.com/%s/status/' % name + str(tweet['id'])
        tweet['href'] = href

    return render_template('tweets.html', record = fetched, median = m_score)


@app.route("/following/<name>")
def following(name):
    """
    Display the list of users followed by a screen name, sorted in
    reverse order by the number of followers of those users.
    """
    fetched_following = fetch_following(api, name)
    sorted_following = sorted(fetched_following, key=lambda k: k['followers'], reverse=True)

    for f in sorted_following:
        f['url'] = "https://twitter.com/%s" % f['screen_name']

    return render_template('following.html', record = sorted_following, name = name)

i = sys.argv.index('server:app')
twitter_auth_filename = sys.argv[i+1] # e.g., "/Users/parrt/Dropbox/licenses/twitter.csv"
api = authenticate(twitter_auth_filename)

# app.run(host='0.0.0.0', port=80)

