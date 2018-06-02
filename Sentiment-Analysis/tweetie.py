import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename)

    auth = tweepy.OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    api = tweepy.API(auth)

    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """

    # n = sum([1 for c in tweepy.Cursor(api.user_timeline, id=name).items(100)])

    tweet_dict = {'user': name}

    tweets_l = []
    n = 0
    for status in tweepy.Cursor(api.user_timeline, id=name).items(100):
        n += 1
        each_status_dict = {}

        hashtags_l = [hashtag['text'] for hashtag in status.entities['hashtags']]
        urls_l = [url['url'] for url in status.entities['urls']]
        mentions = [mention['screen_name'] for mention in status.entities['user_mentions']]

        each_status_dict = {'id': status.id, 'created': status.created_at, 'retweeted': status.retweet_count,
                           'text': status.text, 'hashtags': hashtags_l, 'urls': urls_l, 'mentions': mentions}

        tweets_l.append(each_status_dict)
    tweet_dict['tweets'] = tweets_l
    tweet_dict['count'] = n

    text_l = []
    for tweet in tweet_dict['tweets']:
        text_l.append(tweet['text'])

    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(text)['compound'] for text in text_l]

    for i, tweet in enumerate(tweet_dict['tweets']):
        tweet['score'] = scores[i]

    return tweet_dict


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    following_l = []
    for id in api.friends_ids(name):
        following_dict = {}
        user = api.get_user(id)
        datetime = api.get_user(id).created_at
        following_dict = {'name': user.name, 'screen_name': user.screen_name, 'followers': user.followers_count,
                          'created':str(datetime).split(' ')[0], 'image': user.profile_image_url}
        following_l.append(following_dict)

    return following_l
