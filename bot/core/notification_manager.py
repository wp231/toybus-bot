import discord
from typing import Callable, List
from dao.notification_dao import notification_dao
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class NotificationManager:
    """
    通知管理器
    載入通知資料後啟動通知排程
    """

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.is_started = False
        self.notification_job_id = {}
        self.scheduler = AsyncIOScheduler(timezone="Asia/Taipei")

    async def start(self):
        if self.is_started:
            return

        await self.bot.wait_until_ready()

        self.__load_and_run_notification_job()
        self.scheduler.start()
        self.is_started = True
        

    def stop(self):
        if self.is_started:
            self.scheduler.shutdown()

    def __list_int_to_weekday(self, day_of_week: List[int]) -> str:
        '''將數字轉換為星期幾'''
        weekdays = {
            1: 'mon',
            2: 'tue',
            3: 'wed',
            4: 'thu',
            5: 'fri',
            6: 'sat',
            7: 'sun'
        }
        return ", ".join([weekdays[day] for day in day_of_week])

    def __add_weekly_job(
            self,
            func: Callable,
            day_of_week: List[int],
            hour: int,
            minute: int,
            second: int = 0
    ) -> str:
        '''新增每週排程執行'''
        str_day_of_week = self.__list_int_to_weekday(day_of_week)

        job = self.scheduler.add_job(
            func,
            "cron",
            day_of_week=str_day_of_week,
            hour=hour,
            minute=minute,
            second=second
        )

        return job.id
    

    def __get_send_message_func(self, channel_id: int, message: str)-> Callable:
        '''取得發送訊息的函式'''

        async def send_message():
            channel = await self.bot.fetch_channel(channel_id)
            if isinstance(channel, discord.TextChannel):
                await channel.send(message)

        return send_message
        

    def add_notification_job(self, user_id: int, message: str):
        '''新增通知排程執行'''
        data = notification_dao.get_weekly_notification(user_id, message)
        if data is None:
            return

        job_id = self.__add_weekly_job(
            func=self.__get_send_message_func(data.channel_id, message),
            day_of_week=data.weekdays,
            hour=data.hour,
            minute=data.minute
        )

        self.notification_job_id[user_id][message] = job_id

    def del_notification_job(self, user_id: int, message: str):
        '''刪除通知排程執行'''
        job_id = self.notification_job_id[user_id][message]
        self.scheduler.remove_job(job_id)
        del self.notification_job_id[user_id][message]


    def __load_user_notification_data(self):
        '''載入所有使用者的通知設定'''
        user_ids = notification_dao.get_all_user_id()
        for user_id in user_ids:

            if user_id not in self.notification_job_id:
                self.notification_job_id[user_id] = {}

            messages = notification_dao.get_user_notifications(user_id)
            for message in messages:

                if message not in self.notification_job_id[user_id]:
                    self.notification_job_id[user_id][message] = None

    def __run_notification_job(self):
        '''啟動通知排程，已在排程中的不會重複新增'''
        for user_id, messages in self.notification_job_id.items():
            for message in messages:
                if self.notification_job_id[user_id][message] is None:
                    self.add_notification_job(user_id, message)

    def __load_and_run_notification_job(self):
        '''載入通知設定並啟動通知排程'''
        self.__load_user_notification_data()
        self.__run_notification_job()


if __name__ == "__main__":
    pass
    # notification_manager = NotificationManager()
    # notification_manager.start()

    # notification_manager.add_weekly_job(
    #     lambda: print(f"Current time: {datetime.now()}"),
    #     day_of_week=[1, 2],
    #     hour=0,
    #     minute=0
    # )

    # input("")
    # notification_manager.stop()
