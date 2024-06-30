import os
import sys
import signal
import argparse
import subprocess
from typing import List

TMP_DIR_PATH = "./tmp"
DATA_DIR_PATH = "./data"
PIDS_TMP_FILE_PATH = "./tmp/pids.txt"

SCRIPTS_PATH = [
    "bot/run.py"
]

def init_project_dir():
    # 設定工作目錄
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    os.chdir(current_dir)

    os.makedirs(TMP_DIR_PATH, exist_ok=True)
    os.makedirs(DATA_DIR_PATH, exist_ok=True)

global pids
pids: List[int] = []


def save_pids(file_path: str = PIDS_TMP_FILE_PATH):
    '''保存 PID 到文件'''
    global pids
    with open(file_path, "w") as f:
        for pid in pids:
            f.write(f"{pid}\n")


def load_pids(file_path: str = PIDS_TMP_FILE_PATH):
    '''讀取 PID 文件'''
    global pids
    if os.path.exists(file_path) == False:
        pids = []
        return

    with open(file_path, "r") as f:
        if not f.read().strip():
            pids = []
            return

    with open(file_path, "r") as f:    
        pids = [int(line.strip()) for line in f.readlines()]
        

def pid_manager(func):
    def wrapper(*args, **kwargs):
        load_pids()
        result = func(*args, **kwargs)
        save_pids()
        return result
    return wrapper

@pid_manager
def start_scripts(scripts_path: List[str]):
    '''啟動腳本'''
    global pids

    for script_path in scripts_path:
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        pids.append(process.pid)

@pid_manager
def stop_scripts() -> List[int]:
    '''停止進程

    Return
    ----------
    成功: []
    失敗: 停止失敗的進程
    '''
    global pids

    fail_pids = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            fail_pids.append(pid)

    # 移除停止成功的 PID
    pids = [each for each in pids if each in fail_pids]

    return fail_pids


if __name__ == "__main__":
    init_project_dir()
    load_pids()

    parser = argparse.ArgumentParser(
        description="Controls the operation of the bot.")
    parser.add_argument("command", choices=['start', 'stop', 'restart', 'status'],
                        help="Specifies the command to manage the bot")

    args = parser.parse_args()

    if args.command == "start":
        if pids:
            print("Bot is already running")
            sys.exit(1)

        start_scripts(SCRIPTS_PATH)
        print("Bot has started")

    elif args.command == "stop":
        if not pids:
            print("Bot is not running")
            sys.exit(1)

        fail_pids = stop_scripts()
        
        if not fail_pids:
            print("Bot has stopped")
        else:
            print("Failed to stop the bot")

    elif args.command == "restart":
        if not pids:
            print("Bot is not running")
            sys.exit(1)

        fail_pids = stop_scripts()

        if not fail_pids:
            start_scripts(SCRIPTS_PATH)
            print("Bot has restarted")
        else:
            print("Failed to restart the bot")

    elif args.command == "status":
        if pids:
            print("Bot is running")
        else:
            print("Bot is not running")
