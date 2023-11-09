import tweepy
from datetime import datetime
import json
import threading
import schedule
import numpy as np
import time
import base64
import openai
import re
import json
import os
import psycopg2
import dotenv
import asyncio
import random
import requests
import urllib.request
import pytz
import friendtech
from time import sleep
from web3 import Web3
from friend.program import Program

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

SCENARIO_TOKEN = os.getenv("SCENARIO_TOKEN")
SCENARIO_TOKEN_SECRET = os.getenv("SCENARIO_TOKEN_SECRET")

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")

LIST_IDS = [
    "1699672111399199163",  # Business
    "1699671863658476026",  # AI
    "1698378628877234528"  # Crypto
]

class Tweet:
    def __init__(self, id, text, actioned):
        self.id = id
        self.text = text
        self.actioned = actioned


def main():
    twitter = fetch_v2_api()

   # # Main loop for continuous run
    while True:
        run(twitter)


def run(twitter):
    counter = 0
    while True:
        for list_id in LIST_IDS:
            twitter_timeline = twitter.get_list_tweets(id=list_id, max_results=5)
            formatted_data = format_data(twitter_timeline)
            if formatted_data:
                print(f"formated data: {formatted_data} for list {list_id}")
                insert_to_db(formatted_data)
            else:
                print(f"Empty list")

        tweets = pull_and_action_tweets()

        for tweet in tweets:
            perform_random_action(list_id, tweet, twitter)
            sleep = get_sleep_duration()
            time.sleep(sleep)

        counter += 1


def perform_random_action(list_id, tweet, twitter):

    actions = [
        "like",
        "skip",
        "retweet",
        "emoji",
        "gif",
        "post_photo",
        "post_quote",
        "elon_quote",
        "computer_quote"
    ]
    probabilities = [0.35, 0.20, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]
    action = np.random.choice(actions, p=probabilities)

    action_funcs = {
        "post_photo": lambda: post_photo(twitter),
        "elon_quote": lambda: elon_quote(twitter),
        "computer_quote": lambda: computer_quote(twitter),
        "post_quote": lambda: post_quote(twitter),
        "like": lambda: twitter.like(tweet.id),
        "retweet": lambda: twitter.retweet(tweet.id),
        "emoji": lambda: twitter.create_tweet(
            text=generate_emoji(tweet.text),
            in_reply_to_tweet_id=tweet.id
        ),
        "gif": lambda: twitter.create_tweet(
            text="",
            in_reply_to_tweet_id=tweet.id,
            media_ids=[generate_gif(generate_gif_keywords(tweet.text))]
        ),
        "skip": lambda: None
    }

    action_funcs.get(action, lambda: None)()

    print(f"{action.capitalize()} tweet {tweet.id}")


def get_sleep_duration():
   current_hour = datetime.now().hour
   # Defined sleep and busy hours. Adjust according to requirement.
   sleep_hours = [3,4,5,6,7] # 3AM-7AM
   busy_hours = [8,9,10,11] # 8AM-11AM

   if current_hour in sleep_hours:
       sleepTime = random.choice([1800, 3600, 5400, 7200]) # 30-120 min.
       print(f"Sleeping for {sleepTime} seconds")
   elif current_hour in busy_hours:
       sleepTime = random.choice([300, 600, 900]) # 5-15 min.
       print(f"Sleeping for {sleepTime} seconds")
   else:
       sleepTime = random.choice([600, 1800, 3600]) # 10-60 min.
       print(f"Sleeping for {sleepTime} seconds")

   return sleepTime


def elon_quote(twitter):
    with open('elon.txt') as f:
        lines = f.readlines()

    random_line = random.choice(lines)
    print(random_line)

    text = new_quote(random_line)
    twitter.create_tweet(text=text)
    print(f"Posted quote: {text}")


def computer_quote(twitter):
    with open('quote.txt') as f:
        lines = f.readlines()

    random_line = random.choice(lines)
    print(random_line)

    text = new_quote(random_line)
    twitter.create_tweet(text=text)
    print(f"Posted quote: {text}")


def post_quote(twitter):
    quote = random_quote("Science_Fiction_Final.txt")
    generate_image(quote)
    media_id = upload_photo()
    post_photo(text=quote, media_id=media_id, twitter=twitter)
    print(f"Posted quote: {quote}")


def random_quote(filepath="Science_Fiction_Final.txt"):
    with open(filepath, "r") as file:
        text = file.read()
    quotes = re.findall(r"(.*?\(.*?\))", text, re.DOTALL)
    quotes = [quote for quote in quotes if "—" in quote and quote.strip().endswith(")")]

    while True:
        quote = random.choice(quotes)
        formatted_quote = format_quote(quote)
        if len(formatted_quote) <= 280:
            return formatted_quote


def format_quote(quote):
    idx = quote.find("—")
    summary = " ".join(quote[:idx].strip().split("\n"))
    emoji = generate_emoji(summary)
    summary = summary + " " + "\n\n" + emoji + "\n\n"
    citation = "\n" + quote[idx:].strip()
    return summary + citation


def fetch_v1_api():
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api


def fetch_v2_api():
    api = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )
    return api


def generate_emoji(tweet: str):
    openai.api_key = OPENAI_API_KEY

    prompt = "Respond with three emojis that best encapsulate the essence of this text. Choose symbols that evoke elements of science fiction, mystery, fantastic or mystical phenomena. Only reply with emojis."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + tweet + "\n\n###\n\n",
        temperature=0.7,
        max_tokens=10,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )

    return response.choices[0].text.strip('"')


def new_quote(quote: str):
    openai.api_key = OPENAI_API_KEY

    prompt = """Re-write this quote in your own words.
              Maintain the same themes.
              Do not mention Tesla, SpaceX, PayPal, or any other companies or people by name.
              Be agressive and confrontational, call out failure and weakness.
              The quote will be deliniated with xml tags like this <quote> and </quote>.
              Only reply with the new quote, not the xml tags.
              Your goal is to be exciting and inspiring.
              Your reply must be less than 140 characters.
              Do not use hashtags or emojis."""

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + "<quote>" + quote + "</quote>" + "\n\n###\n\n",
        temperature=0.7,
        max_tokens=120,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )

    return response.choices[0].text.strip('"')


def generate_reply_quote(tweet: str):
    openai.api_key = OPENAI_API_KEY

    prompt = "Write a short one-sententce reply to this text. Be excited and positive.  You want to sound confident and encouraging."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + tweet + "\n\n###\n\n",
        temperature=0.7,
        max_tokens=20,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )

    return response.choices[0].text.strip('"')


def generate_gif_keywords(tweet: str):
    openai.api_key = OPENAI_API_KEY

    prompt = "Respond with three keywords that best encapsulate the essence of this text. Only reply with three keywords."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + tweet + "\n\n###\n\n",
        temperature=0.7,
        max_tokens=10,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )

    return response.choices[0].text.strip('"')


def generate_gif(query):
    """
    Searches for GIFs based on a query
    """
    words = re.findall(r"\w+", query, re.MULTILINE)
    formatted_query = "+".join(words)
    print("Searching for GIFs based on query: ", formatted_query)
    giphy_url = (
        "https://api.giphy.com/v1/gifs/search?api_key="
        + GIPHY_API_KEY
        + "&q="
        + formatted_query
        + "&limit=20&offset=0&rating=r&lang=en"
    )

    with urllib.request.urlopen(giphy_url) as response:
        html = response.read()

    h = html.decode("utf-8")
    gif_info = json.loads(h)
    gif_data = gif_info["data"]
    gif_urls = []
    slugs = []

    for i in range(len(gif_data)):
        gif = gif_data[i]["images"]["downsized"]["url"]
        slug = gif_data[i]["slug"]
        gif_urls.append(gif)
        slugs.append(slug)

    media_id = gif_upload(gif_urls, slugs)
    print("Media ID: ", media_id)
    print("Media String", media_id.media_id_string)
    return media_id.media_id_string


def gif_upload(gif_url_list, msg):
    v1_api = fetch_v1_api()
    """
    uploads a single random GIF and returns the media_id
    """
    random_index = random.randint(
        0, len(gif_url_list) - 1
    )  # Randomly select an index from the gif_url_list

    try:
        gif_download(gif_url_list[random_index])
        m = modifier(msg[random_index])
        media_id = v1_api.media_upload("Photos/image.gif")
        return media_id
    except Exception as e:
        print("Error occurred: ", e)


def gif_download(gif_url):
    """
    Takes the URL of an Image/GIF and downloads it
    """
    gif_data = requests.get(gif_url).content
    with open("Photos/image.gif", "wb") as handler:
        handler.write(gif_data)
        handler.close()


def modifier(s):
    """
    returns hashtags based on the GIF names from GIPHY
    """
    ms = ""
    for i in range(len(s)):
        if s[i] == "-":
            ms += " "
        else:
            ms += s[i]
    ls = ms.split()
    del ls[-1]
    ls[0] = "#" + ls[0]
    return " #".join(ls)


def post_photo(text=None, media_id=None, twitter=None, in_reply_to_tweet_id=None):
    if media_id is None:
        media_id = fetch_random_photo()
    twitter.create_tweet(
        text=text, media_ids=[media_id], in_reply_to_tweet_id=in_reply_to_tweet_id
    )


def fetch_random_photo():
    v1_api = fetch_v1_api()
    random_file = "./Photos/Manga/" + random.choice(os.listdir("./Photos/Manga"))
    result = v1_api.media_upload(random_file)
    return result.media_id_string


def upload_photo(photo_path: str="Photos/reply.jpg"):
    v1_api = fetch_v1_api()
    result = v1_api.media_upload(photo_path)
    return result.media_id_string


def generate_image(tweet: str = None):
    scenario_api_key = base64.b64encode(
        f"{SCENARIO_TOKEN}:{SCENARIO_TOKEN_SECRET}".encode("ascii")
    ).decode("ascii")

    models = [
        "ElMjDKtUSOa8D05BNOtWWQ",
        "KJgC_PKgR02eTTMLOqXeHQ",
        "Y3jhN3_rQyqcL8ELBBazJg",
        "e4g6SIl3S8KOJsUr5Ef2ZQ",
        "WMFVfL6ASISizG1T7X2NNw",
        "DkCC2BfCQ8mhxnyFW1tXcw",
        "IexecVIaRVGzJC49nMb0cA",
    ]
    model_id = random.choice(models)
    colors = ["deep red", "vibrant blue", "vivid green", "royal gold", "purple", "orange", "pink"]
    characters = ["beautiful princess", "space warrior", "alien barbarian", "megalithic computer", "super robot"]
    locations = ["deep space monolith", "desert planet", "prison planet", "cloud city", "cyberpunk jungle world"]

    location = random.choice(locations)
    color = random.choice(colors)
    character = random.choice(characters)

    scene = f"An exciting and cinematic sci-fi image. Use a {color} color palette. The main character is a {character}. The location is a {location}."
    print(scene)

    post_url = f"https://api.cloud.scenario.com/v1/models/{model_id}/inferences"
    payload = {
        "parameters": {
            "type": "txt2img",
            "pageSize": "2",
            "numSamples": "1",
            "prompt": f"{scene} Based on this quote {tweet}",
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Basic {scenario_api_key}",
    }
    response = requests.post(post_url, json=payload, headers=headers)

    while True:
        inference_id = response.json()["inference"]["id"]
        print(f"Waiting for inference {inference_id} to complete")
        get_url = f"https://api.cloud.scenario.com/v1/models/{model_id}/inferences/{inference_id}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Basic {scenario_api_key}",
        }
        response = requests.get(get_url, headers=headers)
        data = json.loads(response.text)
        if data["inference"]["status"] == "succeeded":
            print("Image generated")
            image_url = data["inference"]["images"][0]["url"]
            response = requests.get(image_url)
            with open("Photos/reply.jpg", "wb") as f:
                f.write(response.content)
                print("Downloaded image")
                break

        time.sleep(10)


def database_connect() -> psycopg2.extensions.connection:

    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432",
        database=DB_NAME,
    )
    return conn


def insert_to_db(data):
    conn = database_connect()
    cur = conn.cursor()
    args_str = ','.join(cur.mogrify("(%s,%s,%s)", x).decode('utf-8') for x in data)
    cur.execute(f"INSERT INTO tweets (id, text, actioned) VALUES {args_str} ON CONFLICT (id) DO NOTHING")
    conn.commit()
    cur.close()
    conn.close()

def create_user_table():
    conn = database_connect()
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE friendTech ADD COLUMN address VARCHAR(42)
    """)

   # cur.execute("""
   #     CREATE TABLE friendTech (
   #        userID BIGINT PRIMARY KEY,
   #        userName VARCHAR(255),
   #        actioned BOOLEAN,
   #        date TIMESTAMP
   #     )
   # """)
    conn.commit()
    cur.close()


def pull_and_action_tweets():
    conn = database_connect()
    cur = conn.cursor()

    # Fetch unactioned tweets
    cur.execute("SELECT * FROM tweets WHERE actioned=false LIMIT 5")
    rows = cur.fetchall()

    # Built query to update fetched rows
    ids = [str(x[0]) for x in rows]
    if ids:
        cur.execute(f"UPDATE tweets SET actioned=true WHERE id IN ({','.join(ids)})")

    conn.commit()

    cur.close()
    conn.close()

    return [Tweet(id, text, actioned) for id, text, actioned in rows]


def format_data(twitter_timeline):
    return [(tweet.id, tweet.text, False) for tweet in twitter_timeline.data if not tweet.text.startswith('RT')]


if __name__ == "__main__":
    main()
