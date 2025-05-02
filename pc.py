import os
import re
import time
import random
import threading
import platform
import subprocess
import logging
import sys
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
        print(f"\r{Fore.LIGHTYELLOW_EX}{frames[i % len(frames)]} ⏳ {message}{Style.RESET_ALL}", end="")
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
    """Định dạng thời gian từ giây sang MM:SS."""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def is_valid_tiktok_url(url, mode):
    """Kiểm tra xem URL có phải là URL TikTok hợp lệ không."""
    full_url_pattern = r'^https://www\.tiktok\.com/@[a-zA-Z0-9._]+/video/\d+(\?.*)?$'
    short_url_pattern = r'^https://vt\.tiktok\.com/[a-zA-Z0-9]+/?$'
    profile_url_pattern = r'^https://www\.tiktok\.com/@[a-zA-Z0-9._]+$'
    if mode == "Followers":
        return re.match(profile_url_pattern, url)
    return re.match(full_url_pattern, url) or re.match(short_url_pattern, url)

def display_banner():
    """Hiển thị banner chuyên nghiệp."""
    banner = f"""
    {Fore.LIGHTWHITE_EX}   ██████╗  █████╗  ██████╗ ██████╗ ███████╗     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗╚══███╔╝     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██████╔╝███████║██║   ██║██║  ██║  ███╔╝      {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██╔══██╗██╔══██║██║   ██║██║  ██║ ███╔╝       {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ██████╔╝██║  ██║╚██████╔╝██████╔╝███████╗     {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     {Fore.LIGHTMAGENTA_EX}
                                                       
    {Fore.LIGHTCYAN_EX}   TooL Tích Hợp  - TĂNG TƯƠNG TÁC TỰ ĐỘNG       {Fore.LIGHTMAGENTA_EX}
    {Fore.LIGHTWHITE_EX}   Phiên bản: 1.0.0 | Phát triển: B05 -TooL       {Fore.LIGHTMAGENTA_EX}
    """
    print(banner)

def display_menu(available_modes, mode_status):
    """Hiển thị menu mới đẹp hơn, xóa màn hình trước khi hiển thị."""
    clear_screen()  # Xóa màn hình trước khi hiển thị menu
    print(f"\n{Fore.CYAN}╭{'─' * 40}╮")
    print(f"│{Fore.WHITE}TIKTOK BOT - CHỌN CHẾ ĐỘ TĂNG TƯƠNG TÁC {Fore.CYAN}│")
    print(f"╰{'─' * 40}╯{Style.RESET_ALL}")
    
    for i, mode in enumerate(available_modes, 1):
        icon = {
            "Hearts": "❤️", "Views": "👁️", "Shares": "↗️",
            "Favorites": "⭐", "Followers": "👥", "Live Stream": "📹"
        }.get(mode, "")
        
        status = mode_status.get(mode)
        status_text = "Active" if status == "Active" else "Stop"
        status_color = Fore.GREEN if status == "Active" else Fore.RED
        
        print(f" {Fore.WHITE}{i:>2}. {mode:<15} {icon} {status_color}{status_text}{Style.RESET_ALL}")
    
    while True:
        try:
            print(f"\n{Fore.CYAN}┌{'─' * 20}┐")
            choice = input(f"{Fore.CYAN}│{Fore.WHITE} Chọn chế độ (1-{len(available_modes)}): {Fore.CYAN}│\n{Fore.CYAN}└{'─' * 20}┘\n{Fore.WHITE}➜ {Style.RESET_ALL}")
            
            if not choice.isdigit():
                raise ValueError
            
            mode_choice = int(choice)
            if 1 <= mode_choice <= len(available_modes):
                selected_mode = available_modes[mode_choice - 1]
                if mode_status.get(selected_mode) == "Stop":
                    print(f"\n{Fore.RED}⚠ Chế độ này tạm ngừng hoạt động. Vui lòng chọn chế độ khác.{Style.RESET_ALL}")
                    time.sleep(2)  # Đợi 2 giây để người dùng đọc thông báo
                    return display_menu(available_modes, mode_status)  # Gọi lại menu
                return selected_mode
            print(f"\n{Fore.RED}⚠ Vui lòng nhập số từ 1 đến {len(available_modes)}{Style.RESET_ALL}")
        except ValueError:
            print(f"\n{Fore.RED}⚠ Lỗi: Vui lòng nhập số hợp lệ{Style.RESET_ALL}")

def get_input(prompt, mode=""):
    """Hiển thị ô nhập liệu đẹp hơn"""
    icons = {
        "URL": "🌐",
        "Hearts": "❤️", 
        "Views": "👁️", 
        "Shares": "↗️",
        "Favorites": "⭐", 
        "Followers": "👥"
    }
    icon = icons.get(mode, "✏️")
    prompt_width = len(prompt) + 12
    
    print(f"\n{Fore.CYAN}┌{'─' * prompt_width}┐")
    print(f"│ {icon} {Fore.WHITE}{prompt}{Fore.CYAN} │")
    print(f"└{'─' * prompt_width}╯")
    return input(f"{Fore.WHITE}➜ {Style.RESET_ALL}").strip()

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
        self.last_update_time = time.time()
        self.last_action = time.time()

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
                        EC.presence_of_element_located((By.XPATH, '//img[@class="img-thumbnail card-img-top border-0"]')))
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
                    captcha_text = input(f"{Fore.WHITE}👉 Nhập mã CAPTCHA: {Style.RESET_ALL}")
                    if not captcha_text:
                        log_message("Chưa nhập mã CAPTCHA.", Fore.RED)
                        continue
                    input_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@class="form-control form-control-lg text-center rounded-0 remove-spaces"]')))
                    input_field.clear()
                    input_field.send_keys(captcha_text)
                    try:
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
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

    def update_progress(self, mode, increment):
        """Hiển thị tiến trình với thông tin đã tăng thành công và tổng số."""
        total = getattr(self, f"{mode.lower()}")
        elapsed = int(time.time() - self.start_time)
        
        # Hiển thị tiến trình và xuống dòng ngay
        progress_line = f"{Fore.LIGHTGREEN_EX}✅ Đã tăng: +{increment} {mode} | Tổng: {total} | Thời gian chạy: {format_time(elapsed)}{Style.RESET_ALL}"
        print(progress_line)  # In và tự động xuống dòng

    def wait_with_countdown(self, wait_seconds):
        """Chờ với bộ đếm ngược thời gian thực, hiển thị ngay dưới thông báo trước đó."""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start_wait = time.time()
        while time.time() - start_wait < wait_seconds and self.running:
            elapsed = time.time() - start_wait
            remaining = max(0, wait_seconds - elapsed)
            percent = (elapsed / wait_seconds) * 100
            mins, secs = divmod(int(remaining), 60)
            
            # Hiển thị bộ đếm ngược ngay dưới thông báo trước đó
            countdown_line = f"{Fore.LIGHTYELLOW_EX}{spinner[int(time.time() * 2) % len(spinner)]} Chờ: {mins:02d}:{secs:02d} | Hoàn thành: {percent:.1f}%{Style.RESET_ALL}"
            sys.stdout.write(f"\r{countdown_line}")
            sys.stdout.flush()
            time.sleep(0.1)
        # Xóa dòng bộ đếm ngược
        sys.stdout.write("\r" + " " * 70 + "\r")
        sys.stdout.flush()

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
                "TextBeforeSend": '/html/body/div[12]/div/div/maxspan',
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
                self.last_action = time.time()
                self.update_progress(mode, increment)  # Hiển thị tiến trình và xuống dòng
                self.wait_with_countdown(wait_seconds)  # Hiển thị bộ đếm ngay dưới

                if self.success_count >= 4:
                    rest_time = 600
                    start_rest = time.time()
                    while time.time() - start_rest < rest_time and self.running:
                        remaining = int(rest_time - (time.time() - start_rest))
                        percent = (1 - remaining / rest_time) * 100
                        mins, secs = divmod(remaining, 60)
                        # Hiển thị nghỉ ngay dưới thông báo tăng cuối
                        rest_line = f"{Fore.LIGHTYELLOW_EX}🛑 Nghỉ: {mins:02d}:{secs:02d} | Hoàn thành: {percent:.1f}%{Style.RESET_ALL}"
                        sys.stdout.write(f"\r{rest_line}")
                        sys.stdout.flush()
                        time.sleep(0.1)
                    # Xóa dòng nghỉ
                    sys.stdout.write("\r" + " " * 70 + "\r")
                    sys.stdout.flush()
                    self.success_count = 0

                if (mode == "Views" and self.views >= amount) or \
                   (mode == "Hearts" and self.hearts >= amount) or \
                   (mode == "Shares" and self.shares >= amount) or \
                   (mode == "Favorites" and self.favorites >= amount) or \
                   (mode == "Followers" and self.followers >= amount):
                    log_message(f"🎉 Đã đạt mục tiêu {mode}!", Fore.LIGHTGREEN_EX)
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
    loading_animation("Đang khởi động hệ thống")
    bot = Bot()
    result = bot.setup_bot()
    if not result:
        return
    available_modes, mode_status = result

    while True:
        mode = display_menu(available_modes, mode_status)
        if not mode:
            continue

        mode_vn = {
            "Hearts": "Lượt Thích ❤️", 
            "Views": "Lượt Xem 👁️", 
            "Shares": "Lượt Chia Sẻ ↗️",
            "Favorites": "Lượt Yêu Thích ⭐", 
            "Followers": "Lượt Follow 👥"
        }.get(mode, mode)

        # Nhập URL
        url_prompt = "Nhập URL profile TikTok" if mode == "Followers" else "Nhập URL video TikTok"
        vid_url = get_input(url_prompt, "URL")
        if not is_valid_tiktok_url(vid_url, mode):
            log_message("URL TikTok không hợp lệ. Vui lòng nhập URL video hoặc profile TikTok hợp lệ.", Fore.RED)
            continue

        # Nhập số lượng
        try:
            amount = int(get_input(f"Nhập số lượng {mode_vn}", mode))
            setattr(bot, f"target_{mode.lower()}", amount)  # Lưu mục tiêu
        except ValueError:
            log_message("Số lượng phải là một số.", Fore.RED)
            continue

        print(f"{Fore.LIGHTGREEN_EX}🚀 Bắt đầu tăng {mode_vn}...{Style.RESET_ALL}")
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
            log_message("🛑 Đang dừng bot...", Fore.LIGHTYELLOW_EX)
            bot.stop()
            bot_thread.join()
            log_message("✅ Bot đã dừng thành công.", Fore.LIGHTGREEN_EX)
            print(f"{Fore.LIGHTMAGENTA_EX}╔{'═' * 50}╗{Style.RESET_ALL}")
            print(f"{Fore.LIGHTMAGENTA_EX}║ {Fore.LIGHTWHITE_EX}👉 Nhập URL TikTok mới hoặc 'exit' để thoát: {Style.RESET_ALL}", end="")
            new_url = input().strip().lower()
            print(f"{Fore.LIGHTMAGENTA_EX}╚{'═' * 50}╝{Style.RESET_ALL}")
            if new_url == 'exit':
                break
            if not is_valid_tiktok_url(new_url, mode):
                log_message("URL TikTok không hợp lệ. Vui lòng nhập URL video hoặc profile TikTok hợp lệ.", Fore.RED)
                continue
            vid_url = new_url
            available_modes, mode_status = bot.check_api_status()
            continue

        bot_thread.join()
        log_message(f"{Fore.LIGHTGREEN_EX}🎉 Hoàn thành! Cảm ơn bạn đã sử dụng BaoDz Bot!{Style.RESET_ALL}")
        break

if __name__ == "__main__":
    main()
