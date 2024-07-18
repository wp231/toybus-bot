# 機器人設定

`bot_setting.json` 設定文件用於設定機器人常規設定和管理機器人命令權限

默認先讀取後綴為 `_dev`、`_development`、`_prod`、`_production` 的配置

> 此文件的鍵會在運行後自動生成，請勿手添加鍵

## 使用範例

以下是一個設定文件的範例，展示了如何配置日誌記錄目錄、管理員命令的同步伺服器 ID、可使用管理員命令的身份組，以及如何管理 cog 的使用權限。

```json
{
  "log_dir_path": "./log",           // 日誌記錄目錄（需重啟機器人）
  "admin_guild_ids": [123, 456],     // 管理員命令可同步的伺服器ID（需重啟機器人）
  "admin_role_ids": [123, 456],      // 可使用管理員命令的身份組（需重啟機器人）
  "cog_auth": {                      // 管理 cog 的使用權
    "admin": {                       // admin cog 的使用權（cog 欄位描述）
      "guilds": [123, 456],          // cog 命令要同步到的伺服器
      "roles": [123, 456],           // 能使用 cog 命令的身份組
      "permissions": {},             // 能使用 cog 命令的所需的伺服器權限
      "commands": {}                 // 對 cog 中的命令單獨設定使用權
    },
    "base": {                        // base cog 的使用權（cog 實際示範）
      "guilds": [],                  // 留空同步到全部伺服器
      "roles": [],                   // 留空時不限制身份組，為 `[null]` 時完全禁用該 cog
      "permissions": {},             // 留空時不限制所需的伺服器權限
      "commands": {                  // 對 cog 中的命令單獨設定使用權
        "pong": {                    // 管理 pong 命令的使用權
          "roles": [],               // 能使用命令的身份組，為 `[null]` 時完全禁用該命令
          "permissions": {           // 能使用命令的所需的伺服器權限
            "manage_messages": true  // 需具備編輯消息權限
          }
        }
      }
    }
  }
}
```

> 在 JSON 文件中，註釋是不被允許的。在實際的 JSON 文件中，您應該移除這些註釋。