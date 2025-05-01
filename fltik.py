import requests
import time
import os
import sys
from datetime import datetime

# Clear screen for a clean interface
os.system('cls' if os.name == 'nt' else 'clear')

# ============= PHẦN GIAO DIỆN MỚI =============
def print_banner():
    banner = """
\033[95m\033[1m
  _______ ___   ___  _______  ___      _______  _______ 
 |   _   |   | |   ||       ||   |    |       ||       |
 |  |_|  |   | |   ||    ___||   |    |   _   ||  _____|
 |       |   |_|   ||   |___ |   |    |  | |  || |_____ 
 |       |       _ ||    ___||   |___ |  |_|  ||_____  |
 |   _   |      | ||   |___ |       ||       | _____| |
 |__| |__|____||_||_______||_______||_______||_______|
\033[0m
\033[96m*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*\033[0m
\033[93m🛠️  CÔNG CỤ TĂNG FOLLOW TIKTOK - TIKTOKBUFF PRO\033[0m
\033[92m🔥 Tool siêu múp - POWERED BY BAODZ\033[0m
\033[96m*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*"*\033[0m
"""
    print(banner)
    print(f"\033[93m⏰ Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\033[0m\n")

def print_success(message, count):
    print(f"\033[92m✔ {message} (Lần {count})\033[0m")

def countdown_with_spinner(seconds):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + seconds
    try:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            mins, secs = divmod(remaining, 60)
            percentage = 100 - (remaining / seconds) * 100
            sys.stdout.write(
                f"\r\033[93m{spinner[int(time.time() * 2) % len(spinner)]} Thời gian chờ: {mins:02d}:{secs:02d} | Hoàn thành: {percentage:.1f}%\033[0m"
            )
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()
        sys.exit(0)
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()

# Hiển thị banner chỉ một lần
print_banner()

# Nhập username chỉ một lần trước vòng lặp
username = input('\033[94mNhập Username TikTok (không cần @): \033[0m').strip()
if not username:
    sys.exit(1)

# Biến đếm số lần tăng follow thành công
success_count = 0

# ============= PHẦN CODE CHỨC NĂNG =============
while True:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'vi,fr-FR;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    }
    
    try:
        # Gửi yêu cầu để lấy session và token
        access = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers)
        session = access.cookies.get('ci_session')
        if not session:
            countdown_with_spinner(30)
            continue
        
        headers.update({'cookie': f'ci_session={session}'})
        token = access.text.split("csrf_token = '")[1].split("'")[0]
        data = '{"type":"follow","q":"@' + username + '","google_token":"t","token":"' + token + '"}'
        
        # Gửi yêu cầu tìm kiếm
        search = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data).json()
        
        if search.get('success') == True:
            data_follow = search['data']
            data = '{"google_token":"t","token":"' + token + '","data":"' + data_follow + '","type":"follow"}'
            
            # Gửi yêu cầu tăng follow
            send_follow = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data).json()
            
            if send_follow.get('o') == 'Success!' and send_follow.get('success') == True and send_follow.get('type') == 'success':
                success_count += 1
                print_success('Tăng Follow TikTok thành công!', success_count)
                countdown_from = 900
                countdown_with_spinner(countdown_from)  # 15 phút
                continue
            
            else:
                try:
                    thoigian = send_follow['message'].split('You need to wait for a new transaction. : ')[1].split('.')[0]
                    phut = thoigian.split(' Minutes')[0]
                    giay = int(phut) * 60
                    countdown_from = giay
                    countdown_with_spinner(countdown_from)
                    continue
                except:
                    countdown_from = 30
                    countdown_with_spinner(countdown_from)
                    continue
    
    except:
        countdown_from = 30
        countdown_with_spinner(countdown_from)
        continue