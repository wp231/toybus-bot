import discord
from core.log_viewer import LogPageViewer


class PageNum(discord.ui.Select):
    '''頁數顯示'''

    def __init__(self):
        self.view: LogViewerView
        none = discord.SelectOption(label="None", value="None")
        super().__init__(placeholder="", options=[none], disabled=True)


class PreviousButton(discord.ui.Button):
    def __init__(self):
        self.view: LogViewerView
        super().__init__(label="上一頁", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        self.view.log_page_viewer.prev_page()

        # 更新頁數顯示
        self.view.children[0].placeholder = f"第 {self.view.log_page_viewer._current_page + 1} 頁"

        # 調整按鈕狀態
        if self.view.log_page_viewer._current_page == 0:
            self.disabled = True
        if self.view.children[2].disabled and \
                self.view.log_page_viewer._current_page != self.view.log_page_viewer._page_count - 1:
            self.view.children[2].disabled = False

        # 更新訊息內容
        content = f"```js\n{self.view.log_page_viewer.get_page_content()}\n```"
        await interaction.response.edit_message(content=content, view=self.view)


class NextButton(discord.ui.Button):
    def __init__(self):
        self.view: LogViewerView
        super().__init__(label="下一頁", style=discord.ButtonStyle.blurple, disabled=True)

    async def callback(self, interaction: discord.Interaction):
        self.view.log_page_viewer.next_page()

        # 更新頁數顯示
        self.view.children[0].placeholder = f"第 {self.view.log_page_viewer._current_page + 1} 頁"

        # 更新按鈕狀態
        if self.view.log_page_viewer._current_page == self.view.log_page_viewer._page_count - 1:
            self.disabled = True
        if self.view.children[1].disabled and self.view.log_page_viewer._current_page == 1:
            self.view.children[1].disabled = False

        # 更新訊息內容
        content = f"```js\n{self.view.log_page_viewer.get_page_content()}\n```"
        await interaction.response.edit_message(content=content, view=self.view)


class LogViewerView(discord.ui.View):
    def __init__(self, log_page_viewer: LogPageViewer, timeout: float | None = 300):
        super().__init__(timeout=timeout)
        self.log_page_viewer = log_page_viewer

        self.add_item(PageNum())
        self.add_item(PreviousButton())
        self.add_item(NextButton())

        # 更新頁數顯示
        self.children: list
        self.children[0].placeholder = f"第 {self.log_page_viewer._current_page + 1} 頁"
