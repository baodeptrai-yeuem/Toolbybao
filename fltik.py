import requests
import time
import os
import sys
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

# Kiểm tra nếu đang chạy trên Termux
IS_TERMUX = 'TERMUX_VERSION' in os.environ

# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

# ============= PHẦN GIAO DIỆN =============

def banner():
    """Hiển thị banner chuyên nghiệp."""
    b = f"""
    {Fore.LIGHTWHITE_EX}   ██████╗  █████╗  ██████╗ ██████╗ ███████╗     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗╚══███╔╝     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██████╔╝███████║██║   ██║██║  ██║  ███╔╝      {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██╔══██╗██╔══██║██║   ██║██║  ██║ ███╔╝       {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██████╔╝██║  ██║╚██████╔╝██████╔╝███████╗     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     {Fore.LIGHTMAGENTA_EX}

    {Fore.LIGHTCYAN_EX}   TooL Tích Hợp  - TĂNG TƯƠNG TÁC TỰ ĐỘNG       {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   Phiên bản: 1.0.0 | Phát triển: B05 - TooL    {Fore.LIGHTMAGENTA_EX}
    {Fore.YELLOW}       ⏰ Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    """
    print(b)

def print_success(message, count):
    """In thông báo thành công mà không thêm dòng thừa."""
    # Xóa dòng hiện tại
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()
    # In thông báo thành công, chỉ thêm một dòng mới
    sys.stdout.write(f"{Fore.GREEN}✔ {message} (Lần {count})\n")
    sys.stdout.flush()

def countdown_with_spinner(seconds):
    """Hiển thị đếm ngược với spinner và dọn dẹp sạch sẽ."""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + seconds
    try:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            mins, secs = divmod(remaining, 60)
            percentage = 100 - (remaining / seconds) * 100
            # Xóa dòng hiện tại
            sys.stdout.write("\r" + " " * 70 + "\r")
            sys.stdout.flush()
            # In spinner và đếm ngược
            sys.stdout.write(
                f"{Fore.YELLOW}{spinner[int(time.time() * 2) % len(spinner)]} Thời gian chờ: {mins:02d}:{secs:02d} | Hoàn thành: {percentage:.1f}%"
            )
            sys.stdout.flush()
            time.sleep(0.1)
        # Xóa dòng cuối cùng sau khi đếm ngược xong
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        # Dọn dẹp khi bị gián đoạn
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()
        sys.exit(0)

# Hiển thị banner
banner()

# Nhập username
username = input(f'{Fore.CYAN}Nhập Username TikTok (không cần @): ').strip()
if not username:
    sys.exit(1)

success_count = 0

# ============= PHẦN CHỨC NĂNG =============
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
        access = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers)
        session = access.cookies.get('ci_session')
        if not session:
            countdown_with_spinner(30)
            continue

        headers.update({'cookie': f'ci_session={session}'})
        token = access.text.split("csrf_token = '")[1].split("'")[0]
        data = '{"type":"follow","q":"@' + username + '","google_token":"t","token":"' + token + '"}'

        search = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data).json()

        if search.get('success') == True:
            data_follow = search['data']
            data = '{"google_token":"t","token":"' + token + '","data":"' + data_follow + '","type":"follow"}'

            send_follow = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data).json()

            if send_follow.get('o') == 'Success!' and send_follow.get('success') == True and send_follow.get('type') == 'success':
                success_count += 1
                print_success('Tăng Follow TikTok thành công!', success_count)
                countdown_with_spinner(900)  # 15 phút
                continue
            else:
                try:
                    thoigian = send_follow['message'].split('You need to wait for a new transaction. : ')[1].split('.')[0]
                    phut = thoigian.split(' Minutes')[0]
                    giay = int(phut) * 60
                    countdown_with_spinner(giay)
                    continue
                except:
                    countdown_with_spinner(30)
                    continue

    except:
        countdown_with_spinner(30)
        continue
