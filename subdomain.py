import requests
import sys
import threading
import queue
import os
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_WORDLIST = "subdomains_small.txt"

if len(sys.argv) < 3:
    print(f"{Fore.RED}Usage: python subfinder.py <domain> <threads> [wordlist]")
    sys.exit(1)

host = sys.argv[1].strip()
threads = int(sys.argv[2])
wordlist = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_WORDLIST

if not os.path.exists(wordlist):
    print(f"{Fore.RED}[!] Wordlist not found: {wordlist}")
    sys.exit(1)

q = queue.Queue()
print_lock = threading.Lock()

print(f"\n{Fore.CYAN}[+] Target    : {Fore.YELLOW}{host}")
print(f"{Fore.CYAN}[+] Threads   : {Fore.YELLOW}{threads}")
print(f"{Fore.CYAN}[+] Wordlist  : {Fore.YELLOW}{wordlist}\n")

print(f"{Fore.CYAN}[+] {Style.RESET_ALL}Starting subdomain enumeration...\n")

with open(wordlist, "r") as f:
    for sub in f.read().splitlines():
        if sub:
            q.put(sub)

def subbruteforce():
    session = requests.Session()
    while True:
        try:
            subdomain = q.get_nowait()
        except queue.Empty:
            break

        url = f"http://{subdomain}.{host}"
        try:
            r = session.head(
                url,
                timeout=3,
                allow_redirects=True
            )

            if r.status_code < 400:
                with print_lock:
                    print(f"{Fore.GREEN}[+] Found:{Style.RESET_ALL} ", end="")
                    print(f"{Fore.YELLOW}{subdomain}{Fore.WHITE}.{Fore.CYAN}{host}")

        except requests.RequestException:
            pass

        q.task_done()

for i in range(threads):
    t = threading.Thread(target=subbruteforce, daemon=True)
    t.start()

q.join()
print(f"\n{Fore.GREEN}[+] Scan completed.")
