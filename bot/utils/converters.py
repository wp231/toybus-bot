import discord
from typing import List


def guild_ids_to_guilds(guild_ids: List[int] = []):
    '''轉換伺服器 ID 為 伺服器物件'''
    return [discord.Object(id=guild_id) for guild_id in guild_ids]


def list_to_table(table_list: List[List[str]], split_str: str = '    ') -> str:
    '''輸入二維陣列後進行對齊輸出'''
    try:
        column_width = []
        for i in range(len(table_list[0]) - 1):
            a = [row[i] for row in table_list]
            column_width.append(max(map(len, a)))

        out_str = ""
        for table_row in table_list:
            for i in range(len(table_row) - 1):
                st = table_row[i].ljust(column_width[i])
                out_str = out_str + st + split_str
            out_str = out_str + table_row[-1] + '\n'

        return out_str[:-1]
    except:
        return ""


def pascal_to_snake(name: str) -> str:
    '''將帕斯卡命名法轉換為蛇形命名法'''
    return ''.join(['_' + i.lower() if i.isupper() else i for i in name]).lstrip('_')


def pascal_to_space(s: str) -> str:
    '''將帕斯卡命名法添加空格分隔'''
    if not s:
        return s

    result = [s[0]]
    for char in s[1:]:
        if char.isupper():
            result.append(' ')
        result.append(char)

    return ''.join(result)


if __name__ == "__main__":
    print(guild_ids_to_guilds([1111, 1111]))
