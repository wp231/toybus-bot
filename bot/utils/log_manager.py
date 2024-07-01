import os
import logging
from dao.bot_setting_dao import bot_setting


class LogManager:
    _handlers_added = set()

    def __init__(self, name: str, level=logging.INFO):
        # 避免重複相同日誌
        if name in LogManager._handlers_added:
            self.logger = logging.getLogger(name)
            return

        LogManager._handlers_added.add(name)

        # 創建目錄
        log_path = bot_setting.get_log_dir_path()
        os.makedirs(log_path, exist_ok=True)

        # 定義日誌等級和格式
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        self.formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s:%(message)s",
            datefmt="%m/%d/%Y %H:%M:%S"
        )

        # 創建控制台處理器並設置級別和格式化器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

        # 創建文件處理器並設置級別和格式化器
        log_file_path = os.path.join(log_path, name)
        file_handler = logging.FileHandler(
            f"{log_file_path}.log", mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)


class BotLogManager(LogManager):
    def __init__(self, name: str, level=logging.INFO):
        super().__init__(name, level)

    def info_start(self):
        self.logger.info("Bot is start")

    def info_stop(self):
        self.logger.info("Bot is stop")

    def info_load_cog(self, cog_name):
        self.logger.info(f"Load cog '{cog_name}'")

    def error_load_cog(self, cog_name, error):
        self.logger.error(f"Load cog '{cog_name}'\n{error}")

    def info_cmd_load_cog(self, cog_name, user, user_id):
        self.logger.info(
            f"Command 'load_cog' to load cog '{cog_name}' by {user}({user_id})")

    def error_cmd_load_cog(self, cog_name, user, user_id, error):
        self.logger.error(
            f"Command 'load_cog' to load cog '{cog_name}' by {user}({user_id})\n{error}")

    def info_cmd_reload_cog(self, cog_name, user, user_id):
        self.logger.info(
            f"Command 'reload_cog' to reload cog '{cog_name}' by {user}({user_id})")

    def error_cmd_reload_cog(self, cog_name, user, user_id, error):
        self.logger.error(
            f"Command 'reload_cog' to reload cog '{cog_name}' by {user}({user_id})\n{error}")

    def info_cmd_unload_cog(self, cog_name, user, user_id):
        self.logger.info(
            f"Command  'unload_cog' to unload cog '{cog_name}' by {user}({user_id})")

    def error_cmd_unload_cog(self, cog_name, user, user_id, error):
        self.logger.error(
            f"Command 'unload_cog' to unload cog '{cog_name}' by {user}({user_id})\n{error}")

    def info_sync_command(self, server_name,  command_count, command_table):
        self.logger.info(
            f"Sync {command_count} commands to {server_name}\n{command_table}")

    def error_sync_command(self, server_name, error):
        self.logger.error(f"Failed to sync commands to {server_name}\n{error}")

    def info_cmd_sync_command(self, server_name, user, user_id):
        self.logger.info(
            f"Command 'sync_commands' to sync commands to {server_name} by {user}({user_id})")

    def info_missing_any_role(self, command_name, user, user_id):
        self.logger.info(
            f"User '{user}({user_id})' lacks role to use the '{command_name}' command.")

    def info_no_private_message(self, command_name, user, user_id):
        self.logger.info(
            f"User '{user}({user_id})' misused '{command_name}' command in private message")

    def info_missing_permissions(self, command_name, user, user_id):
        self.logger.info(
            f"User '{user}({user_id})' lacks permissions to use the '{command_name}' command.")

    def info_cmd_stop_bot(self, user, user_id):
        self.logger.info(
            f"Command 'close_bot' to close Bot by {user}({user_id})")

    def info_cmd_restart_bot(self, user, user_id):
        self.logger.info(
            f"Command 'restart_bot' to restart Bot by {user}({user_id})")

    def info_cmd_load_conf(self, user, user_id):
        self.logger.info(
            f"Command 'load_conf' to load bot setting by {user}({user_id})")

    def error_cmd(self, command_name, user, user_id, error):
        self.logger.error(
            f"User '{user}({user_id})' encountered an error using the {command_name}\n{error}")

    def info_cmd_say(self, user, user_id, content, file: bool):
        if file:
            self.logger.info(
                f"Command 'say' to say '{content}' and send file by {user}({user_id})")
        else:
            self.logger.info(
                f"Command 'say' to say '{content}' by {user}({user_id})")

    def error_cmd_say(self, user, user_id, content, file: bool, error):
        if file:
            self.logger.info(
                f"Command 'say' to say '{content}' and send file by {user}({user_id})\n{error}")
        else:
            self.logger.info(
                f"Command 'say' to say '{content}' by {user}({user_id})\n{error}")


bot_log = BotLogManager("bot_info")

if __name__ == "__main__":
    bot_log.error_load_cog("test1", "error1")
    bot_log.error_load_cog("test2", "error2")
