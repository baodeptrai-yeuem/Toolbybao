import requests
import time
import os
import sys
from datetime import datetime
import shutil
from colorama import Fore, init

# Khởi tạo colorama
init()

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
    print(f"\033[92m✔ {message} (Lần {count})\033[0m")  # Chỉ in một lần

def countdown_with_spinner(seconds):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + seconds
    try:
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            mins, secs = divmod(remaining, 60)
            percentage = 100 - (remaining / seconds) * 100
            sys.stdout.write(
                f"\033[93m{spinner[int(time.time() * 2) % len(spinner)]} Thời gian chờ: {mins:02d}:{secs:02d} | Hoàn thành: {percentage:.1f}%\033[0m\r"
            )
            sys.stdout.flush()
            time.sleep(0.1)
        terminal_width = shutil.get_terminal_size().columns
        sys.stdout.write("\r" + " " * terminal_width + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        terminal_width = shutil.get_terminal_size().columns
        sys.stdout.write("\r" + " " * terminal_width + "\r")
        sys.stdout.flush()
        sys.exit(0)

# Hiển thị banner
banner()

# Nhập username
username = input('\033[94mNhập Username TikTok (không cần @): \033[0m').strip()
if not username:
    print("\033[91mLỗi: Vui lòng nhập username!\033[0m")
    sys.exit(1)

# Biến đếm
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
        # Gửi yêu cầu để lấy session và token
        access = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers, timeout=10)
        session = access.cookies.get('ci_session')
        if not session:
            print("\033[91mKhông thể lấy session, thử lại sau 30s...\033[0m")
            countdown_with_spinner(30)
            continue

        headers.update({'cookie': f'ci_session={session}'})
        token = access.text.split("csrf_token = '")[1].split("'")[0]
        data = '{"type":"follow","q":"@' + username + '","google_token":"t","token":"' + token + '"}'

        # Gửi yêu cầu tìm kiếm
        search = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data, timeout=10).json()

        if search.get('success') == True:
            data_follow = search['data']
            data = '{"google_token":"t","token":"' + token + '","data":"' + data_follow + '","type":"follow"}'

            # Gửi yêu cầu tăng follow
            send_follow = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data, timeout=10).json()

            if send_follow.get('o') == 'Success!' and send_follow.get('success') == True and send_follow.get('type') == 'success':
                success_count += 1
                print_success('Tăng Follow TikTok thành công!', success_count)
                countdown_with_spinner(900)  # 15 phút
            else:
                try:
                    thoigian = send_follow['message'].split('You need to wait for a new transaction. : ')[1].split('.')[0]
                    phut = thoigian.split(' Minutes')[0]
                    giay = int(phut) * 60
                    print(f"\033[93mPhải chờ {phut} phút...\033[0m")
                    countdown_with_spinner(giay)
                except:
                    print("\033[91mLỗi không xác định, thử lại sau 30s...\033[0m")
                    countdown_with_spinner(30)
        else:
            print("\033[91mYêu cầu tìm kiếm thất bại, thử lại sau 30s...\033[0m")
            countdown_with_spinner(30)

    except requests.RequestException as e:
        print(f"\033[91mLỗi kết nối: {str(e)}, thử lại sau 30s...\033[0m")
        countdown_with_spinner(30)
    except Exception as e:
        print(f"\033[91mLỗi không mong muốn: {str(e)}, thử lại sau 30s...\033[0m")
        countdown_with_spinner(30)
