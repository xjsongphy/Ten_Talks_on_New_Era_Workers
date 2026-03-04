# 云学堂网课自动观看工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

针对 [byyxt.pupedu.cn](https://byyxt.pupedu.cn) 平台的网课自动观看工具，支持断点续看、浏览器静音和后台播放。

## 快速开始

### 1. 安装依赖

```bash
# 推荐：uv 自动管理虚拟环境
uv sync

# 或 pip
pip install -r requirements.txt
```

### 2. 配置

```bash
cp user.json.example user.json
```

编辑 `user.json`，填入**统一身份认证**的学号和密码：
```json
{
  "user_name": "你的学号",
  "password": "你的密码"
}
```

编辑 `url.md`，填入课程页面完整 URL：
```
https://byyxt.pupedu.cn/xxxxx/d/detailSpu?spu_guid=xxxxx
```

### 3. 运行

```bash
uv run auto_watch
# 或
python main.py
```

程序会自动弹出一个新终端窗口运行 Selenium 服务，随后自动完成登录和观看，全程无需干预。

## 断点续看

- 进度自动保存至 `watch_progress.json`
- 中途按 `Ctrl+C` 中断，下次运行从上次位置继续
- 删除 `watch_progress.json` 可从头开始

## 注意事项

> **运行期间不要关闭自动弹出的 Selenium 服务窗口**，它是浏览器的控制后端，关掉后程序会立即报错退出。

- **Chrome 必须已安装**：程序通过 ChromeDriver 控制浏览器，缺少 Chrome 无法启动；ChromeDriver 本身由 Selenium 4 自动下载，无需手动安装
- **不要手动操作弹出的浏览器**：登录和点击均由程序自动完成，手动干预会打乱页面状态
- **保持电脑不休眠**：休眠会挂起浏览器进程，导致视频暂停和计时中断；建议运行前关闭自动休眠
- **浏览器已静音**：程序启动时自动对 Chrome 静音（`--mute-audio`），不影响视频播放进度统计
- **登录使用统一身份认证**：`user.json` 中填写的是学校统一认证账号，不是平台单独账号

## 项目结构

```
├── auto_watch_courses/
│   ├── auto_watch.py        # 入口：启动服务、登录、观看
│   ├── login.py             # 统一身份认证登录流程
│   ├── watch_courses.py     # 课程列表获取与视频播放
│   ├── selenium_server.py   # Flask + Selenium 控制服务器
│   ├── selenium_client.py   # 命令行调试客户端
│   └── colors.py            # 终端输出格式化
├── main.py                  # python main.py 入口
├── user.json                # 登录信息（不提交）
├── url.md                   # 课程页面 URL
└── watch_progress.json      # 观看进度（自动生成，不提交）
```

## 调试

Selenium 服务运行时，可用客户端手动发送命令：

```bash
python auto_watch_courses/selenium_client.py info              # 当前页面信息
python auto_watch_courses/selenium_client.py find ".h-login"  # 查找元素
python auto_watch_courses/selenium_client.py js "return document.title"  # 执行 JS
```

---

仅供学习研究使用。
