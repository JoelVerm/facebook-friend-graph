from html.parser import HTMLParser
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from tqdm import tqdm
import pickle
import getpass

options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument(
    r"--user-data-dir=C:\Users\joelv\AppData\Local\Google\Chrome\User Data"
)
options.add_argument("--profile-directory=Default")
driver = webdriver.Chrome(options=options)

driver.get("http://www.facebook.com/")

SCROLL_PAUSE_TIME = 2


def get_fb_page(url):
    time.sleep(2)
    driver.get(url)
    time.sleep(2)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    html_source = driver.page_source
    return html_source


def find_friend_from_url(url: str):
    url = url.replace("https://www.facebook.com/", "")
    if url.startswith("profile.php"):
        url = url.replace("profile.php?id=", "")
        url = url.replace("&sk=friends_mutual", "")
        return url
    else:
        url = url.replace("/friends_mutual", "")
        return url


class MyHTMLParser(HTMLParser):
    urls = []

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
            # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    if "friends_mutual" in value:
                        self.urls.append(value)


my_url = "https://www.facebook.com/profile.php?sk=friends"

UNIQ_FILENAME = "uniq_urls.pickle"
uniq_urls = set()
if os.path.isfile(UNIQ_FILENAME):
    with open(UNIQ_FILENAME, "rb") as f:
        uniq_urls = pickle.load(f)
    print(f"We loaded {len(uniq_urls)} unique friends")
else:
    friends_page = get_fb_page(my_url)
    parser = MyHTMLParser()
    parser.feed(friends_page)
    uniq_urls = set(parser.urls)

    print(f"We found {len(uniq_urls)} friends, saving it")

    with open(UNIQ_FILENAME, "wb") as f:
        pickle.dump(uniq_urls, f)

friend_graph = {}
GRAPH_FILENAME = "friend_graph.pickle"

if os.path.isfile(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, "rb") as f:
        friend_graph = pickle.load(f)
    print(f"Loaded existing graph, found {len(friend_graph.keys())} keys")


for url in tqdm(uniq_urls):
    friend_username = find_friend_from_url(url)
    if friend_username not in friend_graph.keys():
        friend_graph[friend_username] = set()

    friend_graph[friend_username].add("You")
    friend_page = get_fb_page(url.replace("friends_mutual", "friends"))

    parser = MyHTMLParser()
    parser.feed(friend_page)
    next_friends_urls = set(parser.urls)

    for next_friend_url in next_friends_urls:
        next_friend = find_friend_from_url(next_friend_url)
        if next_friend not in friend_graph.keys():
            friend_graph[next_friend] = set()
        friend_graph[friend_username].add(next_friend)
        friend_graph[next_friend].add(friend_username)

print(f"We found {len(friend_graph.keys())} friends, saving it")

with open(GRAPH_FILENAME, "wb") as f:
    pickle.dump(friend_graph, f)

driver.quit()
