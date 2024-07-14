import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import pickle

# ! IMPORTANT !
# ! Change this constant into your facebook username !
USERNAME = "J.D. Vermeulen"
# ! IMPORTANT !

options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument(
    r"--user-data-dir=C:\Users\joelv\AppData\Local\Google\Chrome\User Data"
)
options.add_argument("--profile-directory=Default")
driver = webdriver.Chrome(options=options)


def load_entire_page(url):
    driver.get(url)
    last_height = 0

    while True:
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height
    html_source = driver.page_source
    return html_source


def find_friends():
    for link in driver.find_elements(By.XPATH, "//a/img[@height]/.."):
        try:
            friend_url = link.get_attribute("href")
            if "groups" in friend_url:
                continue
            if "profile.php" in friend_url:
                friend_url = friend_url + "&sk=friends"
            else:
                friend_url = friend_url + "/friends"
            friend_name = link.find_element(
                By.XPATH, "../following-sibling::div//span"
            ).text
            yield friend_name, friend_url
        except:
            pass


# Own friends

own_friends_page = "https://www.facebook.com/profile.php?sk=friends"

OWN_FRIENDS_FILENAME = "own_friends.pickle"
own_friends = dict()

if os.path.isfile(OWN_FRIENDS_FILENAME):
    with open(OWN_FRIENDS_FILENAME, "rb") as f:
        own_friends = pickle.load(f)
    print(f"Loaded {len(own_friends)} friends")
else:
    load_entire_page(own_friends_page)

    for friend_name, friend_url in find_friends():
        print(f"{friend_name}: {friend_url}")
        own_friends[friend_name] = friend_url

    print(f"Found {len(own_friends)} friends")

    with open(OWN_FRIENDS_FILENAME, "wb") as f:
        pickle.dump(own_friends, f)

# Friends of friends

friend_graph = {USERNAME: set()}
GRAPH_FILENAME = "friend_graph.pickle"

if os.path.isfile(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, "rb") as f:
        friend_graph = pickle.load(f)
    print(f"Loaded existing graph, found {len(friend_graph.keys())} keys")
else:
    for friend_name, friend_url in own_friends.items():
        friend_graph[USERNAME].add(friend_name)
        if friend_graph.get(friend_name, None) is None:
            friend_graph[friend_name] = set()
        friend_graph[friend_name].add(USERNAME)

        print(friend_name)
        load_entire_page(friend_url)

        for friends_friend_name, friends_friend_url in find_friends():
            print(f"- {friends_friend_name}")
            friend_graph[friend_name].add(friends_friend_name)
            if friend_graph.get(friends_friend_name, None) is None:
                friend_graph[friends_friend_name] = set()
            friend_graph[friends_friend_name].add(friend_name)

    print(f"Found {len(friend_graph.keys())} friends of friends")

    with open(GRAPH_FILENAME, "wb") as f:
        pickle.dump(friend_graph, f)

driver.quit()
