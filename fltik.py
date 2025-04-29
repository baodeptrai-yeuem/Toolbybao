import requests
import time
import re
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Hàm tiện ích
def clear_screen():
    """Xóa màn hình terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def log_message(message, color=Fore.WHITE):
    """Hiển thị thông báo với màu sắc được chỉ định."""
    print(f"{color}{message}{Style.RESET_ALL}")

def divider():
    """Hiển thị gạch phân cách ngang."""
    print(f"{Fore.LIGHTCYAN_EX}════════════════════════════════════════════════{Style.RESET_ALL}")

def format_time(seconds):
    """Định dạng thời gian từ giây sang MM:SS."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes):02d}:{int(seconds):02d}"

def display_banner():
    """Hiển thị banner chuyên nghiệp của BaoDz."""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                BaoDz TikTok Follower Bot             ║
    ║                Tăng Follow TikTok 300M               ║
    ║            Phiên bản: 1.0.0 | Tác giả: BaoDz         ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(Fore.LIGHTCYAN_EX + banner + Style.RESET_ALL)

def display_account_info(username):
    """Hiển thị thông tin tài khoản TikTok với đường gạch phân cách."""
    print(f"{Fore.LIGHTCYAN_EX}════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Tài khoản: @{username}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}════════════════════════════════════════════════{Style.RESET_ALL}")

def main():
    clear_screen()
    display_banner()

    # Nhập thông tin username
    print(f"{Fore.LIGHTCYAN_EX}════════════════════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Nhập Username TikTok (Không nhập @): {Style.RESET_ALL}", end="")
    username = input().strip()
    print(f"{Fore.LIGHTCYAN_EX}════════════════════════════════════════════════{Style.RESET_ALL}")

    if not username:
        log_message("Lỗi: Vui lòng nhập username!", Fore.RED)
        return

    # Hiển thị thông tin tài khoản với đường gạch phân cách
    clear_screen()  # Xóa màn hình trước khi hiển thị thông tin tài khoản
    display_account_info(username)
    divider()  # Thêm gạch phân cách sau thông tin tài khoản

    # Headers cho request
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

    log_message(f"Bắt đầu tăng Follow cho @{username}...", Fore.LIGHTGREEN_EX)

    while True:
        try:
            # Gửi yêu cầu lấy session và token
            access = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers)
            access.raise_for_status()  # Kiểm tra lỗi HTTP

            # Lấy session từ cookie
            session = access.cookies.get('ci_session')
            if not session:
                log_message("Lỗi: Không thể lấy ci_session từ cookie!", Fore.RED)
                time.sleep(5)
                continue

            headers.update({'cookie': f'ci_session={session}'})

            # Lấy token từ nội dung HTML
            token_match = re.search(r"csrf_token = '([^']+)'", access.text)
            if not token_match:
                log_message("Lỗi: Không thể tìm thấy CSRF token!", Fore.RED)
                time.sleep(5)
                continue
            token = token_match.group(1)

            # Gửi yêu cầu tìm kiếm user
            data = f'{{"type":"follow","q":"@{username}","google_token":"t","token":"{token}"}}'
            search = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data).json()

            if search.get('success') != True:
                log_message(f"Lỗi: Không thể tìm thấy @{username} hoặc yêu cầu thất bại!", Fore.RED)
                time.sleep(5)
                continue

            data_follow = search.get('data')
            if not data_follow:
                log_message("Lỗi: Không nhận được data để gửi Follow!", Fore.RED)
                time.sleep(5)
                continue

            # Gửi yêu cầu tăng Follow
            data = f'{{"google_token":"t","token":"{token}","data":"{data_follow}","type":"follow"}}'
            send_follow = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data).json()

            if send_follow.get('o') == 'Success!' and send_follow.get('success') == True and send_follow.get('type') == 'success':
                log_message(f"Thành công: Đã gửi Follow cho @{username}!", Fore.LIGHTGREEN_EX)
                divider()  # Thêm gạch phân cách
                continue

            elif send_follow.get('o') == 'Oops...' and send_follow.get('success') == False and send_follow.get('type') == 'info':
                try:
                    message = send_follow.get('message', '')
                    thoigian_match = re.search(r'You need to wait for a new transaction\. : (\d+) Minutes', message)
                    if not thoigian_match:
                        log_message("Lỗi: Không thể phân tích thời gian chờ từ server!", Fore.RED)
                        time.sleep(5)
                        continue

                    phut = int(thoigian_match.group(1))
                    giay = phut * 60

                    # Bộ đếm ngược thời gian thực
                    for i in range(giay, 0, -1):
                        print(f"\r{Fore.LIGHTYELLOW_EX}Đang chờ: Còn {format_time(i)}...{Style.RESET_ALL}", end='')
                        time.sleep(1)
                    print()
                    divider()  # Thêm gạch phân cách sau khi chờ
                    continue
                except Exception as e:
                    log_message(f"Lỗi: Không thể xử lý thời gian chờ - {str(e)}", Fore.RED)
                    time.sleep(5)
                    continue
            else:
                log_message("Lỗi: Phản hồi từ server không hợp lệ!", Fore.RED)
                time.sleep(5)
                continue

        except requests.exceptions.RequestException as e:
            log_message(f"Lỗi kết nối: {str(e)}", Fore.RED)
            time.sleep(5)
            continue
        except Exception as e:
            log_message(f"Lỗi không xác định: {str(e)}", Fore.RED)
            time.sleep(5)
            continue

if __name__ == "__main__":
    try:
        import requests, colorama, re
    except ImportError:
        log_message("Đang cài đặt các thư viện cần thiết...", Fore.LIGHTYELLOW_EX)
        import os
        os.system("pip install requests colorama")
        log_message("Đã cài đặt thư viện. Vui lòng chạy lại script.", Fore.LIGHTGREEN_EX)
        exit(0)

    try:
        main()
    except KeyboardInterrupt:
        log_message("Đang dừng tool...", Fore.LIGHTYELLOW_EX)
        log_message("Tool đã dừng. Cảm ơn bạn đã sử dụng BaoDz TikTok Follower Bot!", Fore.LIGHTGREEN_EX)
