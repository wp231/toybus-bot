from typing import List


class LogPageViewer:

    def __init__(self, file_path: str, page_char_limit: int) -> None:
        '''讀取檔案，並依照 page_char_limit 進行分頁，初始化頁數、當前頁數
        '''
        with open(file_path, "r", encoding="utf-8") as file:
            log_content = file.read()

        self._pages = self.__split_string_get_pages(
            log_content, page_char_limit)
        self._page_count = len(self._pages)
        self._current_page = len(self._pages) - 1

    def __split_string_get_pages(self, string: str, char_limit: int) -> List[str]:
        '''從末尾提取字串，依 char_limit 進行分頁，以行為斷點'''
        pages = []
        string = string.strip()

        while len(string) > char_limit:
            if string[-char_limit - 1] == "\n":
                page = string[-char_limit:]
                string = string[:-char_limit]

            else:
                split_point = string.find("\n", -char_limit)
                if split_point == -1:
                    split_point = -char_limit
                else:
                    split_point += 1
                page = string[split_point:]
                string = string[:split_point]

            pages.append(page)

            while string[-1] in [" ", "\n"]:
                string = string[:-1]

        pages.append(string)
        pages.reverse()

        return pages

    def get_page_content(self) -> str:
        '''取得當前頁面內容'''
        return self._pages[self._current_page]

    def prev_page(self) -> None:
        '''翻到上一頁'''
        if self._current_page > 0:
            self._current_page -= 1

    def next_page(self) -> None:
        '''翻到下一頁'''
        if self._current_page < self._page_count - 1:
            self._current_page += 1
