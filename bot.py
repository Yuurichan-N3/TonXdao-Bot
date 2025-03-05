import sys
import json
import requests
import os
import time
from queue import Queue
import threading
from tabulate import tabulate
from termcolor import colored

# Menonaktifkan pembuatan bytecode
sys.dont_write_bytecode = True

# Implementasi manual untuk modul base
class Base:
    @staticmethod
    def file_path(file_name):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)

    @staticmethod
    def create_line(length):
        return "-" * length

    @staticmethod
    def create_banner(game_name):
        return f"\n=== {game_name} Automation Tool ===\n"

    @staticmethod
    def clear_terminal():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def log(message):
        pass  # Semua log di luar tabel dihapus

    # Warna untuk log
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    white = "\033[97m"
    magenta = "\033[95m"
    cyan = "\033[96m"

base = Base()

# Konfigurasi disisipkan langsung ke dalam script
CONFIG = {
    "auto_check_in": True,
    "auto_do_task": True,
    "auto_farm": True,
    "auto_join_syndicate": True,
    "target_syndicate_name": "Sentinel"
}

# Definisikan headers
def headers(token=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://app.production.tonxdao.app",
        "Referer": "https://app.production.tonxdao.app/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# Modul token
def get_token(data, proxies=None):
    if not data or not isinstance(data, str):
        return None, "Unknown"
    url = "https://app.production.tonxdao.app/api/v1/login/web-app"
    payload = {"initData": data}
    try:
        response = requests.post(url=url, headers=headers(), json=payload, proxies=proxies, timeout=20)
        data = response.json()
        token = data["access_token"]
        username = data.get("user", {}).get("username", "Unknown")
        return token, username
    except:
        return None, "Unknown"

def get_centrifugo_token(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/centrifugo-token"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        token = data["token"]
        return token
    except:
        return None

# Modul info
def get_info(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/profile"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        dao_id = data["dao_id"]
        coins = data["coins"]
        energy = data["energy"]
        max_energy = data["max_energy"]
        return {"dao_id": dao_id, "coins": coins, "energy": energy, "max_energy": max_energy}
    except:
        return None

# Modul task
def check_in(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/tasks/daily"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        status = data["is_available"]
        return status
    except:
        return None

def claim_check_in(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/tasks/daily/claim"
    try:
        response = requests.post(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        status = data["success"]
        return status
    except:
        return None

def process_check_in(token, proxies=None):
    check_in_status = check_in(token=token, proxies=proxies)
    if check_in_status:
        start_check_in = claim_check_in(token=token, proxies=proxies)
        if start_check_in:
            return "Success"
        return "Fail"
    return "Claimed"

def get_task(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/tasks"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        return data
    except:
        return None

def start_task(token, task_id, proxies=None):
    url = f"https://app.production.tonxdao.app/api/v1/tasks/{task_id}/start"
    try:
        response = requests.post(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        return data
    except:
        return None

def claim_task(token, task_id, proxies=None):
    url = f"https://app.production.tonxdao.app/api/v1/tasks/{task_id}/claim"
    try:
        response = requests.post(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        return data
    except:
        return None

def process_do_task(token, proxies=None):
    task_list = get_task(token=token, proxies=proxies)
    if task_list:
        for task in task_list:
            task_id = task["id"]
            task_name = task["name"]
            is_active = task["is_active"]
            is_started = task["is_started"]
            is_completed = task["is_completed"]
            is_claimed = task["is_claimed"]
            if is_active:
                if is_started:
                    if is_completed:
                        if is_claimed:
                            return "Completed"
                        else:
                            start_claim = claim_task(token=token, task_id=task_id, proxies=proxies)
                            return "Claiming..."
                    else:
                        return "Not ready to claim"
                else:
                    do_task = start_task(token=token, task_id=task_id, proxies=proxies)
                    return "Starting..."
            else:
                return "Inactive"
    return "N/A"

# Modul syndicate dan voting
def search_syndicate(token, syndicate_name="Sentinel", proxies=None):
    url = f"https://app.production.tonxdao.app/api/v1/syndicates?search_query={syndicate_name.replace(' ', '%20')}"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        if data and len(data) > 0:
            return data[0]["id"]
        return None
    except:
        return None

def join_syndicate(token, syndicate_id, proxies=None):
    url = f"https://app.production.tonxdao.app/api/v1/syndicates/{syndicate_id}/join"
    try:
        response = requests.post(url=url, headers=headers(token=token), json={"code": "join_syndicate"}, proxies=proxies, timeout=20)
        data = response.json()
        return data.get("success", False)
    except:
        return False

def get_last_voting_id(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/last-voting-id"
    try:
        response = requests.get(url=url, headers=headers(token=token), proxies=proxies, timeout=20)
        data = response.json()
        return data.get("id", None) if data and "id" in data else None
    except:
        return None

def vote_on_voting(token, voting_id, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/voting"
    payload = {
        "voting_id": voting_id,
        "code": "join_syndicate",
        "vote_decision": "yes"
    }
    try:
        response = requests.post(url=url, headers=headers(token=token), json=payload, proxies=proxies, timeout=20)
        data = response.json()
        return data["success"] if "success" in data else False
    except:
        return False

# Modul ws
class WebSocketRequest:
    def __init__(self):
        self.ws = None
        self.message_id = 1
        self.connected = False
        self.response_queue = Queue()
        self.dao_id = None
        self.current_energy = 0

    def connect_websocket(self, token, dao_id):
        self.dao_id = dao_id
        self.token = token
        import websocket
        self.ws = websocket.WebSocketApp(
            "wss://ws.production.tonxdao.app/ws",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        self.start_sync_loop()

    def on_open(self, ws):
        self.connected = True
        self.send_message({"connect": {"token": self.token, "name": "js"}, "id": self.message_id})

    def on_message(self, ws, message):
        self.response_queue.put(message)

    def on_error(self, ws, error):
        pass

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False

    def send_message(self, message):
        if self.connected:
            self.ws.send(json.dumps(message))
            self.message_id += 1

    def get_response(self, timeout=10):
        try:
            response = self.response_queue.get(timeout=timeout)
            return json.loads(response)
        except Queue.Empty:
            return None

    def start_sync_loop(self):
        def sync_loop():
            while self.connected:
                sync_response = self.sync_request()
                if sync_response and "rpc" in sync_response and "data" in sync_response["rpc"]:
                    energy = sync_response["rpc"]["data"]["energy"]
                    self.current_energy = energy
                time.sleep(5)
        threading.Thread(target=sync_loop, daemon=True).start()

    def sync_request(self):
        self.send_message({"rpc": {"method": "sync", "data": {}}, "id": self.message_id})
        return self.get_response()

    def publish_request(self):
        self.send_message({"publish": {"channel": f"dao:{self.dao_id}", "data": {}}, "id": self.message_id})
        return self.get_response()

def process_farm(token, dao_id):
    ws_request = WebSocketRequest()
    ws_request.connect_websocket(token, dao_id)
    while not ws_request.connected:
        time.sleep(0.1)
    connection_response = ws_request.get_response()
    initial_energy = ws_request.current_energy
    simulated_energy = initial_energy

    while ws_request.connected:
        try:
            publish_response = ws_request.publish_request()
            sync_response = ws_request.sync_request()
            if sync_response and "rpc" in sync_response and "data" in sync_response["rpc"]:
                coins = sync_response["rpc"]["data"]["coins"]
                dao_coins = sync_response["rpc"]["data"]["dao_coins"]
                simulated_energy = ws_request.current_energy

                if simulated_energy > 0:
                    simulated_energy -= 1
                    ws_request.current_energy = simulated_energy

                return {"coins": coins, "dao_coins": dao_coins, "energy": simulated_energy}
        except:
            break
        time.sleep(1)
    
    return {"coins": 0, "dao_coins": 0, "energy": 0}

# Script utama (TONxDAO)
class TONxDAO:
    def __init__(self):
        self.data_file = base.file_path(file_name="data.txt")
        self.line = base.create_line(length=50)
        self.banner = base.create_banner(game_name="TONxDAO")
        self.auto_check_in = CONFIG["auto_check_in"]
        self.auto_do_task = CONFIG["auto_do_task"]
        self.auto_farm = CONFIG["auto_farm"]
        self.auto_join_syndicate = CONFIG["auto_join_syndicate"]
        self.target_syndicate_name = CONFIG["target_syndicate_name"]
        self.account_status = []

    def process_join_syndicate_and_vote(self, token, dao_id, proxies=None):
        if not self.auto_join_syndicate:
            return

        syndicate_id = search_syndicate(token, self.target_syndicate_name, proxies)
        if not syndicate_id:
            return

        join_success = join_syndicate(token, syndicate_id, proxies)
        if not join_success:
            return

        time.sleep(2)

        voting_id = get_last_voting_id(token, proxies)
        if voting_id:
            vote_on_voting(token, voting_id, proxies)

    def update_account_status(self, data, index):
        token, username = get_token(data) if get_token(data) is not None else (None, "Unknown")
        if not data or not token:
            self.account_status[index] = {
                "no": index + 1,
                "token_status": "Failed",
                "check_in": "N/A",
                "username": username,
                "farm": "N/A",
                "coins": 0,
                "energy": 0
            }
            return
        try:
            info = get_info(token) or {}
            dao_id = info.get("dao_id", None)
            if not dao_id:
                self.account_status[index] = {
                    "no": index + 1,
                    "token_status": "Failed",
                    "check_in": "N/A",
                    "username": username,
                    "farm": "N/A",
                    "coins": 0,
                    "energy": 0
                }
                return
            centrifugo_token = get_centrifugo_token(token)
            check_in_result = process_check_in(token) if self.auto_check_in else "ON"
            farm_result = process_farm(centrifugo_token, dao_id) if self.auto_farm else {"coins": 0, "dao_coins": 0, "energy": info.get("energy", 0)}
            self.process_join_syndicate_and_vote(token, dao_id)  # Jalankan join dan vote tanpa status

            self.account_status[index] = {
                "no": index + 1,
                "token_status": "Success",
                "check_in": "Success" if self.auto_check_in and check_in_result == "Success" else check_in_result,
                "username": username if username != "Unknown" else "N/A",
                "farm": "ON" if self.auto_farm and farm_result["energy"] >= 5 else "ON",
                "coins": farm_result["coins"] or info.get("coins", 0),
                "energy": farm_result["energy"] or info.get("energy", 0)
            }
        except Exception as e:
            self.account_status[index] = {
                "no": index + 1,
                "token_status": "Failed",
                "check_in": "N/A",
                "username": username if username != "Unknown" else "N/A",
                "farm": "N/A",
                "coins": 0,
                "energy": 0
            }

    def display_status_table(self):
        base.clear_terminal()
        print("╔══════════════════════════════════════════════╗")
        print("║       🌟 TONxDAO Automation Tool 🌟          ║")
        print("║   Automate your TONxDAO account tasks!       ║")
        print("║  Developed by: https://t.me/sentineldiscus   ║")
        print("╚══════════════════════════════════════════════╝")
        table_data = []
        for account in self.account_status:
            no = account.get("no", "N/A")
            token_status = account.get("token_status", "N/A")
            check_in = account.get("check_in", "N/A")
            username = account.get("username", "N/A")
            farm = account.get("farm", "N/A")
            coins = account.get("coins", 0)
            energy = account.get("energy", 0)

            table_data.append([
                no,
                colored(token_status, "magenta"),
                colored(check_in, "magenta"),
                colored(username, "cyan"),
                colored(farm, "magenta"),
                colored(f"{coins:,.0f}", "cyan"),
                colored(str(energy), "cyan")
            ])
        print(tabulate(table_data, headers=["No", "Token Status", "Check-in", "Username", "Farm", "Coins", "Energy"], tablefmt="fancy_grid"))

    def main(self):
        try:
            threads = []
            while True:
                try:
                    data = open(self.data_file, "r").read().splitlines()
                    num_acc = len(data)
                    self.account_status = [{} for _ in range(num_acc)]

                    for index, account_data in enumerate(data):
                        thread = threading.Thread(target=self.update_account_status, args=(account_data, index))
                        threads.append(thread)
                        thread.start()

                    for thread in threads:
                        thread.join()

                    self.display_status_table()
                    time.sleep(10)
                    threads = []

                except FileNotFoundError:
                    pass
                except KeyboardInterrupt:
                    pass
                except Exception:
                    pass

        except Exception:
            pass

if __name__ == "__main__":
    try:
        txd = TONxDAO()
        txd.main()
    except KeyboardInterrupt:
        sys.exit()
