import os
from dotenv import load_dotenv


def init_env() -> None:
    '''初始化環境變數'''
    env_file_priority = [
        ".env.dev",
        ".env.development",
        ".env.prod",
        ".env.production",
        ".env"
    ]

    for filename in env_file_priority:
        if os.path.exists(filename):
            load_dotenv(dotenv_path=filename)
            return


def get_config_file_path(file_path: str) -> str:
    """優先級檢查並獲取配置文件

    Return
    -------
    返回優先高的路徑
    不存在則返回原路徑
    """
    config_file_priority = [
        "dev",
        "development",
        "prod",
        "production"
    ]

    file_path = os.path.normpath(file_path)

    path, filename = os.path.split(file_path)
    filename, extension = os.path.splitext(filename)

    for file in config_file_priority:
        tmp_filename = f"{filename}_{file}{extension}"
        tmp_path = os.path.join(path, tmp_filename)
        if os.path.isfile(tmp_path):
            return tmp_path

    return file_path


if __name__ == "__main__":
    print(get_config_file_path("./data/bot_setting.json"))

    init_env()
    print(os.getenv('BOT_TOKEN'))
