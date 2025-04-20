from typing import List
from dao.base_dao import BaseDAO
from utils.utils import get_config_file_path

NOTIFICATION_FILE_PATH = get_config_file_path("./data/notification.json")


class UserNotificationDataStruct:
    def __init__(self, hour: int, minute: int, weekdays: List[int], channel_id: int) -> None:
        self.hour = hour
        self.minute = minute
        self.weekdays = weekdays
        self.channel_id = channel_id


class NotificationDAO(BaseDAO):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)

    @staticmethod
    def __auto_save(func):
        '''自動讀取、寫入檔案'''

        def wrapper(self, *args, **kwargs):
            self.read()
            result = func(self, *args, **kwargs)
            self.write()
            return result
        return wrapper

    @staticmethod
    def __auto_read(func):
        '''自動讀取檔案'''

        def wrapper(self, *args, **kwargs):
            self.read()
            return func(self, *args, **kwargs)
        return wrapper

    @__auto_save
    def __create_user(self, user_id: str) -> None:
        self.jdata[user_id] = {}

    @__auto_save
    def add_weekly_notification(
        self,
        user_id: int,
        message: str,
        hour: int,
        minute: int,
        weekdays: List[int],
        channel_id: int
    ) -> None:
        '''添加記錄用戶設定的每周提醒'''

        str_user_id = str(user_id)
        if str_user_id not in self.jdata:
            self.__create_user(str_user_id)

        self.jdata[str_user_id][message] = {
            "hour": hour,
            "minute": minute,
            "weekdays": weekdays,
            "channel_id": channel_id
        }

    @__auto_read
    def get_weekly_notification(self, user_id: int, message: str) -> UserNotificationDataStruct | None:
        '''取得用戶設定的每周提醒'''

        if str(user_id) not in self.jdata:
            return None

        try:
            return UserNotificationDataStruct(
                hour=self.jdata[str(user_id)][message]["hour"],
                minute=self.jdata[str(user_id)][message]["minute"],
                weekdays=self.jdata[str(user_id)][message]["weekdays"].copy(),
                channel_id=self.jdata[str(user_id)][message]["channel_id"]
            )
        except Exception:
            return None

    @__auto_read
    def get_all_user_id(self) -> List[int]:
        '''取得所有用戶 ID'''
        return [int(user_id) for user_id in self.jdata.keys()]

    @__auto_read
    def get_user_notifications(self, user_id: int) -> List[str]:
        '''取得用戶設定的所有通知'''
        if str(user_id) not in self.jdata:
            return []

        return list(self.jdata[str(user_id)].keys())
    
    @__auto_save
    def del_user_notification(self, user_id: int, message: str) -> None:
        '''刪除用戶設定的通知'''
        str_user_id = str(user_id)
        if str_user_id in self.jdata and message in self.jdata[str_user_id]:
            del self.jdata[str_user_id][message]
            if not self.jdata[str_user_id]:
                del self.jdata[str_user_id]


notification_dao = NotificationDAO(NOTIFICATION_FILE_PATH)
