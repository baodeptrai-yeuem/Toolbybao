import os
import re
import time
import random
import threading
import platform
import subprocess
import logging
try:
    import chromedriver_autoinstaller
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from PIL import Image
    from colorama import init, Fore, Style
    import customtkinter as ctk
    import tkinter as tk
    import pytesseract
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Thư viện {e.name} chưa được cài đặt. Đang cài đặt các thư viện cần thiết...")
    os.system("pip install customtkinter selenium Pillow pytesseract chromedriver-autoinstaller beautifulsoup4")
    print("Đã cài đặt các thư viện. Vui lòng chạy lại script.")
    exit(0)

# Khởi tạo colorama
init(autoreset=True)

# Tắt log của Selenium, ChromeDriver và urllib3
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('webdriver').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Hàm tiện ích
def clear_screen():
    """Xóa màn hình terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def log_message(message, color=Fore.WHITE):
    """Hiển thị thông báo với màu sắc được chỉ định."""
    print(f"{color}{message}{Style.RESET_ALL}")

def loading_animation(message, duration=2):
    """Hiển thị hiệu ứng loading với dấu chấm động."""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.LIGHTYELLOW_EX}{frames[i % len(frames)]} {message}{Style.RESET_ALL}", end="")
        i += 1
        time.sleep(0.1)
    print()

def open_image_in_termux(file_path):
    """Mở hình ảnh trong Termux bằng termux-open."""
    try:
        if not os.path.exists(file_path):
            log_message(f"Lỗi: Không tìm thấy file {file_path}.", Fore.RED)
            return False
        result = subprocess.run(["termux-open", file_path], capture_output=True, text=True)
        if result.returncode == 0:
            log_message("Đã mở hình CAPTCHA. Vui lòng kiểm tra trong trình xem mặc định.", Fore.LIGHTYELLOW_EX)
            log_message("Sau khi xem, nhấn nút Quay lại trên điện thoại để trở về Termux và nhập mã CAPTCHA.", Fore.LIGHTYELLOW_EX)
            return True
        else:
            log_message(f"Lỗi khi mở hình trong Termux: {result.stderr}", Fore.RED)
            return False
    except Exception as e:
        log_message(f"Lỗi khi mở hình trong Termux: {e}", Fore.RED)
        return False

def is_termux():
    """Kiểm tra xem script có chạy trong Termux không."""
    return "termux" in os.environ.get("SHELL", "").lower() or "com.termux" in os.environ.get("PREFIX", "").lower()

def format_time(seconds):
    """Định dạng thời gian từ giây sang HH:MM:SS."""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def is_valid_tiktok_url(url, mode):
    """Kiểm tra xem URL có phải là URL TikTok hợp lệ không."""
    full_url_pattern = r'^https://www\.tiktok\.com/@[a-zA-Z0-9._]+/video/\d+(\?.*)?$'
    short_url_pattern = r'^https://vt\.tiktok\.com/[a-zA-Z0-9]+/?$'
    profile_url_pattern = r'^https://www\.tiktok\.com/@[a-zA-Z0-9._]+$'
    if mode == "Followers":
        return re.match(profile_url_pattern, url)
    return re.match(full_url_pattern, url) or re.match(short_url_pattern, url)

def display_banner():
    """Hiển thị banner chuyên nghiệp của BaoDz."""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                 BaoDz Zefoy Bot - TikTok             ║
    ║        Tăng Views, Hearts, Shares, Followers         ║
    ║             Phiên bản: 1.0.0 | Tác giả: BaoDz        ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(Fore.LIGHTCYAN_EX + banner + Style.RESET_ALL)

def display_menu(available_modes, mode_status):
    """Hiển thị menu lựa chọn chế độ với trạng thái màu sắc."""
    clear_screen()
    display_banner()
    print(f"{Fore.LIGHTCYAN_EX}┌────────────────── Chọn Chế Độ ──────────────────┐{Style.RESET_ALL}")
    for i, mode in enumerate(available_modes, 1):
        mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", 
                   "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream", 
                   "Followers": "Lượt Follow"}.get(mode, mode)
        status = mode_status.get(mode, "Stop")
        color = Fore.LIGHTGREEN_EX if status == "Active" else Fore.RED
        status_text = "Active" if status == "Active" else "Stopped due to out of API"
        print(f"{color}│ {i}. {mode_vn:<36} ({status_text}) │{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}└─────────────────────────────────────────────────┘{Style.RESET_ALL}")
    print(f"{Fore.WHITE}│ Nhập số chế độ: {Style.RESET_ALL}", end="")

class Bot:
    def __init__(self):
        self.driver = None
        self.running = False
        self.views = 0
        self.hearts = 0
        self.shares = 0
        self.favorites = 0
        self.followers = 0
        self.start_time = time.time()
        self.success_count = 0

    def check_api_status(self):
        """Kiểm tra trạng thái API của tất cả các chế độ."""
        mode_status = {}
        available_modes = ["Hearts", "Views", "Shares", "Favorites", "Live Stream", "Followers"]
        buttons = {
            "Hearts": '//button[contains(@class, "t-hearts-button")]',
            "Views": '//button[contains(@class, "t-views-button")]',
            "Shares": '//button[contains(@class, "t-shares-button")]',
            "Favorites": '//button[contains(@class, "t-favorites-button")]',
            "Live Stream": '//button[contains(@class, "t-livestream-button")]',
            "Followers": '//button[@class="btn btn-primary rounded-0 t-followers-button"]'
        }

        for text, xpath in buttons.items():
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                mode_status[text] = "Active" if not button.get_attribute("disabled") else "Stop"
            except Exception:
                mode_status[text] = "Stop"
        
        return available_modes, mode_status

    def setup_bot(self):
        loading_animation("Đang khởi tạo bot")
        chromedriver_autoinstaller.install()
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-webgl")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(log_path=os.devnull, service_args=["--silent"])
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            log_message(f"Lỗi khởi tạo Chrome: {e}", Fore.RED)
            return False

        self.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["https://fundingchoicesmessages.google.com/*"]})
        self.driver.execute_cdp_cmd("Network.enable", {})
        if not self.get_captcha():
            log_message("Không thể giải CAPTCHA. Thoát.", Fore.RED)
            return False

        return self.check_api_status()

    def get_captcha(self):
        url = "http://zefoy.com"
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            for attempt in range(3):
                try:
                    captcha_img_tag = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//img[@class="img-thumbnail card-img-top border-0"]'))
                    )
                    captcha_img_tag.screenshot('captcha.png')
                    log_message("Đã lưu CAPTCHA thành captcha.png", Fore.LIGHTGREEN_EX)
                    if is_termux():
                        if not open_image_in_termux('captcha.png'):
                            log_message("Không thể mở hình CAPTCHA. Vui lòng mở captcha.png thủ công để xem.", Fore.RED)
                    try:
                        above_captcha = self.driver.find_element(By.XPATH, '//div[contains(@class, "card-body")]//p')
                        above_text = above_captcha.text
                        log_message(f"Văn bản phía trên CAPTCHA: {above_text}", Fore.LIGHTYELLOW_EX)
                    except:
                        log_message("", Fore.LIGHTYELLOW_EX)
                    captcha_text = input(f"{Fore.WHITE}Nhập mã CAPTCHA: {Style.RESET_ALL}")
                    if not captcha_text:
                        log_message("Chưa nhập mã CAPTCHA.", Fore.RED)
                        continue
                    input_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@class="form-control form-control-lg text-center rounded-0 remove-spaces"]'))
                    )
                    input_field.clear()
                    input_field.send_keys(captcha_text)
                    try:
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
                        )
                        submit_button.click()
                    except:
                        log_message("Không tìm thấy hoặc không cần nút gửi.", Fore.LIGHTYELLOW_EX)
                    time.sleep(3)
                    if self.driver.find_elements(By.XPATH, '/html/body/div[6]/div/div[2]/div/div/div[1]'):
                        log_message("CAPTCHA được chấp nhận.", Fore.LIGHTGREEN_EX)
                        return True
                    else:
                        log_message("CAPTCHA không đúng, thử lại...", Fore.LIGHTYELLOW_EX)
                        self.driver.refresh()
                        time.sleep(3)
                except Exception as e:
                    log_message(f"Thử lần {attempt + 1} thất bại: {e}", Fore.RED)
                    if attempt < 2:
                        time.sleep(3)
                    else:
                        return False
        except Exception as e:
            log_message(f"Lỗi khi giải CAPTCHA: {e}", Fore.RED)
            return False

    def check_hearts_api(self):
        """Kiểm tra xem API Hearts có khả dụng không."""
        try:
            button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "t-hearts-button")]'))
            )
            return not button.get_attribute("disabled")
        except:
            return False

    def wait_for_api(self, check_interval=300):
        """Chờ cho đến khi API khả dụng trở lại."""
        log_message("API đang hết. Đang đợi...", Fore.LIGHTYELLOW_EX)
        while self.running:
            start_wait = time.time()
            while time.time() - start_wait < check_interval and self.running:
                remaining = int(check_interval - (time.time() - start_wait))
                print(f"\r{Fore.LIGHTYELLOW_EX}Đang đợi API: Còn {format_time(remaining)}{Style.RESET_ALL}", end='')
                time.sleep(1)
            print()
            self.driver.refresh()
            if self.check_hearts_api():
                log_message("API đã khả dụng! Tiếp tục chạy.", Fore.LIGHTGREEN_EX)
                return True
            log_message("API vẫn chưa khả dụng. Tiếp tục đợi...", Fore.LIGHTYELLOW_EX)

    def parse_wait_time(self, text):
        """Phân tích thời gian chờ từ văn bản."""
        match = re.search(r'(\d+) minute\(s\) (\d{1,2}) second\(s\)', text)
        if not match:
            match = re.search(r'(\d+) minute\(s\) (\d{1,2}) seconds', text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds + 2
        log_message(f"Không thể phân tích thời gian chờ: {text}", Fore.RED)
        return 0

    def wait_with_countdown(self, wait_seconds):
        """Chờ với bộ đếm ngược thời gian thực."""
        start_wait = time.time()
        while time.time() - start_wait < wait_seconds and self.running:
            elapsed = time.time() - self.start_time
            remaining = int(wait_seconds - (time.time() - start_wait))
            future_time = format_time(elapsed + remaining)
            print(f"\r{Fore.LIGHTCYAN_EX}Thời gian chạy: {format_time(elapsed)} | Chờ: {Fore.WHITE}{remaining}s (đến {future_time})){Style.RESET_ALL}", end='')
            time.sleep(1)
        print()

    def increment_mode_count(self, mode):
        """Tăng số lượng tương ứng với chế độ."""
        if mode == "Views":
            self.views += 500
            return 500
        elif mode == "Hearts":
            increment = random.randint(11, 15)
            self.hearts += increment
            return increment
        elif mode == "Shares":
            increment = random.randint(70, 80)
            self.shares += increment
            return increment
        elif mode == "Favorites":
            increment = random.randint(3, 6)
            self.favorites += increment
            return increment
        elif mode == "Followers":
            increment = random.randint(3, 6)
            self.followers += increment
            return increment
        return 0

    def display_total(self, mode):
        """Trả về chuỗi tổng số của chức năng hiện tại với màu vàng pha xanh lá cây."""
        mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", 
                   "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream", 
                   "Followers": "Lượt Follow"}.get(mode, mode)
        if mode == "Views":
            total = self.views
        elif mode == "Hearts":
            total = self.hearts
        elif mode == "Shares":
            total = self.shares
        elif mode == "Favorites":
            total = self.favorites
        elif mode == "Followers":
            total = self.followers
        else:
            total = 0
        return f"{Fore.LIGHTYELLOW_EX} | Tổng số {mode_vn}: {Fore.GREEN}{total}{Style.RESET_ALL}"

    def loop(self, vidUrl, mode, amount):
        data = {
            "Hearts": {
                "MainButton": '//button[@class="btn btn-primary rounded-0 t-hearts-button"]',
                "Input": '/html/body/div[8]/div/form/div/input',
                "Send": '/html/body/div[8]/div/div/div[1]/div/form/button',
                "Search": '/html/body/div[8]/div/form/div/div/button',
                "TextBeforeSend": '/html/body/div[8]/div/div/span',
                "TextAfterSend": '/html/body/div[8]/div/div/span[1]'
            },
            "Views": {
                "MainButton": '//button[@class="btn btn-primary rounded-0 t-views-button"]',
                "Input": '/html/body/div[10]/div/form/div/input',
                "Send": '/html/body/div[10]/div/div/div[1]/div/form/button',
                "Search": '/html/body/div[10]/div/form/div/div/button',
                "TextBeforeSend": '/html/body/div[10]/div/div/span',
                "TextAfterSend": '/html/body/div[10]/div/div/span[1]'
            },
            "Shares": {
                "MainButton": '//button[@class="btn btn-primary rounded-0 t-shares-button"]',
                "Input": '/html/body/div[11]/div/form/div/input',
                "Send": '/html/body/div[11]/div/div/div[1]/div/form/button',
                "Search": '/html/body/div[11]/div/form/div/div/button',
                "TextBeforeSend": '/html/body/div[11]/div/div/span',
                "TextAfterSend": '/html/body/div[11]/div/div/span[1]'
            },
            "Favorites": {
                "MainButton": '//button[@class="btn btn-primary rounded-0 t-favorites-button"]',
                "Input": '/html/body/div[12]/div/form/div/input',
                "Send": '/html/body/div[12]/div/div/div[1]/div/form/button',
                "Search": '/html/body/div[12]/div/form/div/div/button',
                "TextBeforeSend": '/html/body/div[12]/div/div/span',
                "TextAfterSend": '/html/body/div[12]/div/div/span[1]'
            },
            "Followers": {
                "MainButton": '//button[@class="btn btn-primary rounded-0 t-followers-button"]',
                "Input": '/html/body/div[9]/div/form/div/input',
                "Send": '/html/body/div[9]/div/div/div[1]/div/form/button',
                "Search": '/html/body/div[9]/div/form/div/div/button',
                "TextBeforeSend": '/html/body/div[9]/div/div/span',
                "TextAfterSend": '/html/body/div[9]/div/div/span[1]'
            },
        }

        while self.running and (
            (mode == "Views" and self.views < amount) or 
            (mode == "Hearts" and self.hearts < amount) or 
            (mode == "Shares" and self.shares < amount) or 
            (mode == "Favorites" and self.favorites < amount) or 
            (mode == "Followers" and self.followers < amount)
        ):
            try:
                self.driver.refresh()
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(2)
                main_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, data[mode]["MainButton"]))
                )
                main_button.click()
                time.sleep(2)
                input_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, data[mode]["Input"]))
                )
                input_field.send_keys(vidUrl)
                time.sleep(2)
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, data[mode]["Search"]))
                )
                search_button.click()
                time.sleep(6)
                wait_text = self.driver.find_element(By.XPATH, data[mode]["TextBeforeSend"]).text
                if wait_text:
                    wait_seconds = self.parse_wait_time(wait_text)
                    if wait_seconds > 0:
                        self.wait_with_countdown(wait_seconds)
                        self.driver.refresh()
                        continue
                send_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, data[mode]["Send"]))
                )
                send_button.click()
                time.sleep(7)
                wait_text = self.driver.find_element(By.XPATH, data[mode]["TextAfterSend"]).text
                wait_seconds = self.parse_wait_time(wait_text)
                increment = self.increment_mode_count(mode)
                self.success_count += 1
                mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", 
                           "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream", 
                           "Followers": "Lượt Follow"}.get(mode, mode)
                success_message = f"Thành công: Đã thêm {increment} {mode_vn}!"
                total_message = self.display_total(mode)
                log_message(f"{success_message}{total_message}", Fore.LIGHTGREEN_EX)

                if self.success_count >= 5:
                    log_message("Đã gửi 5 lần. Nghỉ 10 phút...", Fore.LIGHTYELLOW_EX)
                    rest_time = 600
                    start_rest = time.time()
                    while time.time() - start_rest < rest_time and self.running:
                        remaining = int(rest_time - (time.time() - start_rest))
                        print(f"\r{Fore.LIGHTYELLOW_EX}Đang nghỉ: Còn {format_time(remaining)}{Style.RESET_ALL}", end='')
                        time.sleep(1)
                    print()
                    self.success_count = 0

                self.wait_with_countdown(wait_seconds)

                if (mode == "Views" and self.views >= amount) or \
                   (mode == "Hearts" and self.hearts >= amount) or \
                   (mode == "Shares" and self.shares >= amount) or \
                   (mode == "Favorites" and self.favorites >= amount) or \
                   (mode == "Followers" and self.followers >= amount):
                    log_message(f"Đã đạt giới hạn {mode_vn}: {amount}", Fore.LIGHTYELLOW_EX)
                    self.running = False
                    break
            except Exception as e:
                log_message(f"Lỗi trong chế độ {mode}: {e}", Fore.RED)
                self.driver.refresh()
                time.sleep(5)

    def stop(self):
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

def main():
    clear_screen()
    display_banner()
    loading_animation("Đang khởi động")
    bot = Bot()
    result = bot.setup_bot()
    if not result:
        return
    available_modes, mode_status = result

    while True:
        display_menu(available_modes, mode_status)
        try:
            mode_choice = int(input())
            if 1 <= mode_choice <= len(available_modes):
                mode = available_modes[mode_choice - 1]
                if mode_status.get(mode) == "Stop":
                    mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", 
                               "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream", 
                               "Followers": "Lượt Follow"}.get(mode, mode)
                    log_message(f"Chế độ {mode_vn} hiện không khả dụng (Stopped due to out of API). Vui lòng chọn chế độ khác.", Fore.RED)
                    continue
            else:
                log_message(f"│ Lựa chọn không hợp lệ. Vui lòng chọn số từ 1 đến {len(available_modes)}.", Fore.RED)
                continue
        except ValueError:
            log_message("│ Vui lòng nhập một số hợp lệ.", Fore.RED)
            continue

        print(f"{Fore.LIGHTCYAN_EX}══════════════════════════════════════════════{Style.RESET_ALL}")
        url_prompt = "Nhập URL profile TikTok: " if mode == "Followers" else "Nhập URL video TikTok: "
        print(f"{Fore.WHITE}{url_prompt}{Style.RESET_ALL}", end="")
        vid_url = input().strip()
        if not is_valid_tiktok_url(vid_url, mode):
            log_message("URL TikTok không hợp lệ. Vui lòng nhập URL video hoặc profile TikTok hợp lệ.", Fore.RED)
            continue
        mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", 
                   "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream", 
                   "Followers": "Lượt Follow"}.get(mode, mode)
        print(f"{Fore.WHITE}Nhập số lượng {mode_vn}: {Style.RESET_ALL}", end="")
        try:
            amount = int(input())
        except ValueError:
            log_message("Số lượng phải là một số.", Fore.RED)
            continue
        print(f"{Fore.LIGHTCYAN_EX}══════════════════════════════════════════════{Style.RESET_ALL}")

        print(f"{Fore.LIGHTGREEN_EX}Bắt đầu tăng {mode_vn}...{Style.RESET_ALL}")
        bot.running = True
        bot.start_time = time.time()
        bot.views = 0
        bot.hearts = 0
        bot.shares = 0
        bot.favorites = 0
        bot.followers = 0
        bot.success_count = 0

        bot_thread = threading.Thread(target=bot.loop, args=(vid_url, mode, amount))
        bot_thread.start()

        try:
            while bot.running:
                time.sleep(1)
        except KeyboardInterrupt:
            log_message("Đang dừng bot...", Fore.LIGHTYELLOW_EX)
            bot.stop()
            bot_thread.join()
            log_message("Bot đã dừng.", Fore.LIGHTGREEN_EX)
            print(f"{Fore.LIGHTCYAN_EX}══════════════════════════════════════════════{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Nhập URL TikTok mới: {Style.RESET_ALL}", end="")
            new_url = input().strip()
            print(f"{Fore.LIGHTCYAN_EX}══════════════════════════════════════════════{Style.RESET_ALL}")
            if not is_valid_tiktok_url(new_url, mode):
                log_message("URL TikTok không hợp lệ. Vui lòng nhập URL video hoặc profile TikTok hợp lệ.", Fore.RED)
                continue
            vid_url = new_url
            available_modes, mode_status = bot.check_api_status()  # Cập nhật trạng thái API
            continue

        bot_thread.join()
        log_message("Cảm ơn bạn đã sử dụng BaoDz Zefoy Bot!", Fore.LIGHTGREEN_EX)
        break

if __name__ == "__main__":
    main()
