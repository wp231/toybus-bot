# 開發規範

此文件用於規範機器人的開發規範，包括命名規範、檔案結構、Cog 規範等。

## 命名規範

- **檔案名稱**: 使用小寫字母，單字之間使用底線分隔
  - 例: `example_file.py`
- **變數名稱**: 使用小寫字母，單字之間使用底線分隔
  - 例: `example_variable`
- **函數名稱**: 使用小寫字母，單字之間使用底線分隔
  - 例: `example_function`
- **類別名稱**: 使用大寫字母開頭的駝峰式命名
  - 例: `ExampleClass`
- **常數名稱**: 使用大寫字母，單字之間使用底線分隔
  - 例: `EXAMPLE_CONSTANT`

## Bot 結構

`bot` 資料夾為機器人的主要程式碼

- **bot**
  - **cogs**: Cog 檔案
  - **core**: 機器人核心程式碼
  - **dao**: 資料庫存取物件
  - **utils**: 輔助工具程式碼
  - **run.py**: 機器人運行程式碼

## Cog 說明

- Cog 的檔案保存在 `bot/cogs` 資料夾中
- Cog 資料夾中的檔案將自被機器人偵測，可使用 `/load_cog` 指令載入

### Cog 規範

- Cog 的`類名`必須與該 Cog 的`檔名`相同
- 類別必須繼承 `CogExtension` 類別
- 在 `setup` 函數中，必須加入 `await bot.add_cog(CogName(bot))`，以載入 Cog
- `CogName` 類別中必須包含 `check = CommandChecker()`
  - `CommandChecker` 是檢查器，用於檢查指令是否符合條件
  - 指令函數必須加上 `@check.roleauth` 裝飾器，以檢查是否符合條件
  - 檢查器會自動生成屬於該 Cog 和 Command 的權限設定位

以下為 `cog_name.py` 的範例：

```python
import discord
from run import Bot
from discord import app_commands
from core.cog_utils import CogExtension, CommandChecker

# Cog 名稱需和檔案名稱相同，採用駝峰式命名
class CogName(CogExtension):
    __doc__ = "Cog 描述"
    check = CommandChecker()

    @check.roleauth  # check.roleauth 為檢查器，用於檢查指令是否符合條件
    @app_commands.command(name="cmd", description="description")
    async def cmd(self, interaction: discord.Interaction):
        pass

# 在 setup 函數中載入 Cog
async def setup(bot: Bot):
    await bot.add_cog(CogName(bot))
```
