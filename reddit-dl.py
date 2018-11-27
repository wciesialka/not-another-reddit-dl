import praw
import configparser
import requests
import os
from tqdm import tqdm

CONFIG = configparser.ConfigParser()
CONFIG_SECTION = 'USER_DETAILS'
CONFIG_FILE = 'auth_config.cfg'
AUTH =  {"client_id": None, "client_secret": None, "password": None, "user_agent": "not-another-reddit-dl", "username": None}
REDDIT = None
IMAGE_ENDINGS = [".png",".jpg",".jpeg",".gif"]
POST_COUNT = 0

def is_image(post):
    url = post.url
    v = False
    for ending in IMAGE_ENDINGS:
        if(url.endswith(ending)):
            v = True
    return v

def intput(prompt,fallback=None):
    try:
        v = int(input(prompt))
    except:
        if fallback:
            return fallback
        else:
            print("Must be int value.")
            return intput(prompt)
    else:
        return v

def download(url,filename=None,directory=None):
    try:
        if not filename:
            filename = url[url.rfind("/"):url.rfind(".")]
        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        extension = url[url.rfind("."):]
        if not directory:
            directory = os.getcwd()
        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
        _file = f"{filename}{extension}"
        fullpath = os.path.join(directory,_file)
        response = requests.get(url,stream=True)
        with open(fullpath,"wb") as f:
            for data in response:
                f.write(data)
    except:
        raise

def main():
    directory = input("Directory to save to, defaults to cwd: ") or os.getcwd()
    score_lim = intput("Lower score limit, defaults to 1: ",fallback=1)
    sub = input("Take from subreddit /r/")
    posts = REDDIT.subreddit(sub).top('all',limit=None)
    try:
        for post in tqdm(posts,desc=f"/r/{sub}",unit="posts"):
            if(post.score >= score_lim):
                if(is_image(post)):
                    try:
                        download(post.url,directory=f"{directory}/{sub}")
                    except:
                        print(f"Failed to download \'{post.title}\'")
    except:
        print(f"Could not get data from subreddit /r/{sub}. Check to see if the subreddit exists and that you are connected to the internet.")

def input_auth():
    for field in AUTH:
        if not AUTH[field]:
            AUTH[field] = input(field + ": ")

def fill_auth():
    try:
        CONFIG.read_file(open(CONFIG_FILE))
    except:
        print(f"\'{CONFIG_FILE}\' not found.")
        CONFIG[CONFIG_SECTION] = {}
        input_auth()
        for field in AUTH:
            CONFIG[CONFIG_SECTION][field] = AUTH[field]
    else:
        for field in AUTH:
            AUTH[field] = CONFIG[CONFIG_SECTION][field]
    finally:
        with open(CONFIG_FILE, 'w+') as configfile:
            CONFIG.write(configfile)

fill_auth()
REDDIT = praw.Reddit(client_id = AUTH["client_id"], client_secret = AUTH["client_secret"], user_agent = AUTH["user_agent"])

if __name__ == "__main__":
    main()
