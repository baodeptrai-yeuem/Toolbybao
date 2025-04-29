import os
import re
import time
import random
import threading
import platform
import subprocess
import logging
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from colorama import init, Fore, Style

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

def is_valid_tiktok_url(url):
    """Kiểm tra xem URL có phải là URL video TikTok hợp lệ không."""
    # Kiểm tra URL đầy đủ (https://www.tiktok.com/@username/video/video_id)
    full_url_pattern = r'^https://www\.tiktok\.com/@[a-zA-Z0-9._]+/video/\d+(\?.*)?$'
    # Kiểm tra URL rút gọn (https://vt.tiktok.com/some_id/)
    short_url_pattern = r'^https://vt\.tiktok\.com/[a-zA-Z0-9]+/?$'

    if re.match(full_url_pattern, url) or re.match(short_url_pattern, url):
        return True
    return False

def display_banner():
    """Hiển thị banner chuyên nghiệp của BaoDz."""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                 BaoDz Zefoy Bot - TikTok             ║
    ║                Tăng Views, Hearts, Shares            ║
    ║             Phiên bản: 1.0.0 | Tác giả: BaoDz        ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(Fore.LIGHTCYAN_EX + banner + Style.RESET_ALL)

def display_menu(available_modes):
    """Hiển thị menu lựa chọn chế độ chuyên nghiệp."""
    clear_screen()
    display_banner()
    print(f"{Fore.LIGHTCYAN_EX}┌────────────────── Chọn Chế Độ ──────────────────┐{Style.RESET_ALL}")
    for i, mode in enumerate(available_modes, 1):
        mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream"}.get(mode, mode)
        print(f"{Fore.LIGHTGREEN_EX}│ {i}. {mode_vn:<40} │{Style.RESET_ALL}")
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
        self.start_time = time.time()
        self.success_count = 0

    def setup_bot(self):
        loading_animation("Đang khởi tạo bot")
        chromedriver_autoinstaller.install()

        # Cấu hình Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-webgl")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Tắt log của ChromeDriver
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

        available_modes = []
        buttons = {
            "Hearts": '//button[contains(@class, "t-hearts-button")]',
            "Views": '//button[contains(@class, "t-views-button")]',
            "Shares": '//button[contains(@class, "t-shares-button")]',
            "Favorites": '//button[contains(@class, "t-favorites-button")]',
            "Live Stream": '//button[contains(@class, "t-livestream-button")]'
        }

        for text, xpath in buttons.items():
            try:
                button = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if not button.get_attribute("disabled"):
                    available_modes.append(text)
                else:
                    if text == "Hearts":
                        log_message("API Lượt Thích hiện đang hết. Bot sẽ kiểm tra lại sau.", Fore.LIGHTYELLOW_EX)
                log_message(f"Đã tìm thấy nút {text}", Fore.LIGHTCYAN_EX)
            except Exception as e:
                log_message(f"Lỗi tìm nút {text}: {e}", Fore.RED)

        if not available_modes:
            log_message("Không tìm thấy chế độ nào khả dụng. Kiểm tra cấu trúc trang hoặc kết nối mạng.", Fore.RED)
            return False

        return available_modes

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
        """Chờ cho đến khi API Hearts khả dụng trở lại."""
        log_message("API Lượt Thích đang hết. Đang đợi...", Fore.LIGHTYELLOW_EX)
        while self.running:
            start_wait = time.time()
            while time.time() - start_wait < check_interval and self.running:
                remaining = int(check_interval - (time.time() - start_wait))
                print(f"\r{Fore.LIGHTYELLOW_EX}Đang đợi API Lượt Thích: Còn {format_time(remaining)}{Style.RESET_ALL}", end='')
                time.sleep(1)
            print()
            self.driver.refresh()
            if self.check_hearts_api():
                log_message("API Lượt Thích đã khả dụng! Tiếp tục chạy.", Fore.LIGHTGREEN_EX)
                return True
            log_message("API Lượt Thích vẫn chưa khả dụng. Tiếp tục đợi...", Fore.LIGHTYELLOW_EX)

    def parse_wait_time(self, text):
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
        if mode == "Views":
            self.views += 500  # Chỉ tăng 500 lượt xem mỗi lần
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
        return 0

    def display_total(self, mode):
        """Hiển thị tổng số của chức năng hiện tại."""
        mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream"}.get(mode, mode)
        if mode == "Views":
            total = self.views
        elif mode == "Hearts":
            total = self.hearts
        elif mode == "Shares":
            total = self.shares
        elif mode == "Favorites":
            total = self.favorites
        else:
            total = 0
        log_message(f"Tổng số {mode_vn}: {total}", Fore.LIGHTMAGENTA_EX)

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
        }

        while self.running and (self.views < amount or self.hearts < amount or self.shares < amount or self.favorites < amount):
            # Kiểm tra API Hearts nếu đang ở chế độ Hearts
            if mode == "Hearts" and not self.check_hearts_api():
                self.wait_for_api()
                if not self.running:
                    break
                continue

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

                # Tăng số đếm và hiển thị thông báo
                increment = self.increment_mode_count(mode)
                self.success_count += 1
                mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream"}.get(mode, mode)
                log_message(f"Thành công: Đã thêm {increment} {mode_vn}!", Fore.LIGHTGREEN_EX)
                self.display_total(mode)  # Hiển thị tổng số của chức năng hiện tại

                # Kiểm tra nếu đã gửi 5 lần thành công
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
                   (mode == "Favorites" and self.favorites >= amount):
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
                pass  # Bỏ qua lỗi khi đóng driver để tránh hiển thị thông báo lỗi

def main():
    clear_screen()
    display_banner()
    loading_animation("Đang khởi động")

    # Thiết lập bot và lấy danh sách chế độ
    bot = Bot()
    available_modes = bot.setup_bot()
    if not available_modes:
        return

    # Hiển thị menu lựa chọn chế độ
    display_menu(available_modes)
    try:
        mode_choice = int(input())
        if 1 <= mode_choice <= len(available_modes):
            mode = available_modes[mode_choice - 1]
        else:
            log_message(f"│ Lựa chọn không hợp lệ. Vui lòng chọn số từ 1 đến {len(available_modes)}.", Fore.RED)
            bot.stop()
            return
    except ValueError:
        log_message("│ Vui lòng nhập một số hợp lệ.", Fore.RED)
        bot.stop()
        return

    # Lấy thông tin từ người dùng
    print(f"{Fore.LIGHTCYAN_EX}┌────────────────── Nhập Thông Tin ───────────────┐{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}|                                                 |{Style.RESET_ALL}")
    vid_url = input(f"{Fore.WHITE}│ Nhập URL video TikTok:                           {Style.RESET_ALL}").strip()
    # Kiểm tra URL TikTok hợp lệ
    if not is_valid_tiktok_url(vid_url):
        log_message("│ URL TikTok không hợp lệ. Vui lòng nhập URL video TikTok hợp lệ.", Fore.RED)
        bot.stop()
        return
    mode_vn = {"Hearts": "Lượt Thích", "Views": "Lượt Xem", "Shares": "Lượt Chia Sẻ", "Favorites": "Lượt Yêu Thích", "Live Stream": "Live Stream"}.get(mode, mode)
    try:
        amount = int(input(f"{Fore.WHITE}│ Nhập số lượng {mode_vn:<32} {Style.RESET_ALL}"))
    except ValueError:
        log_message("│ Số lượng phải là một số.", Fore.RED)
        bot.stop()
        return
    print(f"{Fore.LIGHTCYAN_EX}|                                                 |{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}└─────────────────────────────────────────────────┘{Style.RESET_ALL}")

    # Khởi chạy bot
    print(f"{Fore.LIGHTGREEN_EX}Bắt đầu tăng {mode_vn}...{Style.RESET_ALL}")
    bot.running = True
    bot.start_time = time.time()

    # Chạy bot trong luồng riêng
    bot_thread = threading.Thread(target=bot.loop, args=(vid_url, mode, amount))
    bot_thread.start()

    # Xử lý khi người dùng dừng bot
    try:
        while bot.running:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("Đang dừng bot...", Fore.LIGHTYELLOW_EX)
        bot.stop()
        log_message("Bot đã dừng. Cảm ơn bạn đã sử dụng BaoDz Zefoy Bot!", Fore.LIGHTGREEN_EX)

if __name__ == "__main__":
    try:
        import selenium, chromedriver_autoinstaller, colorama, PIL
    except ImportError:
        log_message("Đang cài đặt các thư viện cần thiết...", Fore.LIGHTYELLOW_EX)
        os.system("pip install selenium chromedriver_autoinstaller colorama pillow")
        log_message("Đã cài đặt thư viện. Vui lòng chạy lại script.", Fore.LIGHTGREEN_EX)
        exit(0)
    main()
