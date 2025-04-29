import requests
import time
import os

# Clear screen for a clean interface
os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("\033[1;36m" + "="*50 + "\033[0m")
    print("\033[1;36m|\033[0m" + " TikTok Follower Booster ".center(48) + "\033[1;36m|\033[0m")
    print("\033[1;36m" + "="*50 + "\033[0m")

def print_success(message):
    print("\033[1;32m✔ " + message + "\033[0m")

def print_error(message):
    print("\033[1;31m✘ " + message + "\033[0m")

def print_waiting(seconds):
    print(f"\033[1;33m⏳ Vui lòng chờ {seconds} giây...\033[0m", end='\r')

print_header()
username = input('\033[1;34mNhập Username TikTok (không cần @): \033[0m')

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
    
    access = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers)
    
    try:
        session = access.cookies['ci_session']
        headers.update({'cookie': f'ci_session={session}'})
        token = access.text.split("csrf_token = '")[1].split("'")[0]
        data = '{"type":"follow","q":"@' + username + '","google_token":"t","token":"' + token + '"}'
        
        search = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data).json()
        
        if search['success'] == True:
            data_follow = search['data']
            data = '{"google_token":"t","token":"' + token + '","data":"' + data_follow + '","type":"follow"}'
            send_follow = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data).json()
            
            if send_follow['o'] == 'Success!' and send_follow['success'] == True and send_follow['type'] == 'success':
                print_success('Tăng Follow TikTok thành công! Vào TikTok kiểm tra ngay!')
                continue
            
            elif send_follow['o'] == 'Oops...' and send_follow['success'] == False and send_follow['type'] == 'info':
                try:
                    thoigian = send_follow['message'].split('You need to wait for a new transaction. : ')[1].split('.')[0]
                    phut = thoigian.split(' Minutes')[0]
                    giay = int(phut) * 60
                    
                    for i in range(giay, 0, -1):
                        print_waiting(i)
                        time.sleep(1)
                    print(" " * 50, end='\r')  # Clear waiting message
                    continue
                
                except:
                    print_error('Lỗi không xác định. Thử lại...')
                    continue
    
    except:
        print_error('Lỗi không xác định. Thử lại...')
        continue
