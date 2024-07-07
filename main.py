import os
import sys
import signal
import git.cmd
import argparse
import subprocess
from typing import List

TMP_DIR_PATH = "./tmp"
DATA_DIR_PATH = "./data"
PIDS_TMP_FILE_PATH = "./tmp/pids.txt"

SCRIPTS_PATH = [
    "bot/run.py"
]

global pids
pids: List[int] = []


def init_project_dir():
    # 設定工作目錄
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    os.chdir(current_dir)

    os.makedirs(TMP_DIR_PATH, exist_ok=True)
    os.makedirs(DATA_DIR_PATH, exist_ok=True)


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

    pids = []

    return fail_pids


def update_scripts():
    '''更新腳本'''
    stop_scripts()

    g = git.cmd.Git(".")

    branch = g.branch("-r")
    if "origin/main" in branch:
        g.pull("origin", "main")
    elif "origin/master" in branch:
        g.pull("origin", "master")
    else:
        print("No main or master branch found")
        sys.exit(1)

    start_scripts(SCRIPTS_PATH)


if __name__ == "__main__":
    init_project_dir()
    load_pids()

    parser = argparse.ArgumentParser(description="Bot manager")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("start", help="Start the bot")
    subparsers.add_parser("stop", help="Stop the bot")
    subparsers.add_parser("restart", help="Restart the bot")
    subparsers.add_parser("status", help="Check the bot status")
    subparsers.add_parser("update", help="Update the bot")

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
            print(f"Failed to stop the bot: {fail_pids}")

    elif args.command == "restart":
        if not pids:
            print("Bot is not running")
            sys.exit(1)

        stop_scripts()
        start_scripts(SCRIPTS_PATH)
        print("Bot has restarted")

    elif args.command == "status":
        if pids:
            print("Bot is running")
        else:
            print("Bot is not running")

    elif args.command == "update":
        print("Bot is updating...")
        update_scripts()
        print("Bot has updated")

    else:
        parser.print_help()
