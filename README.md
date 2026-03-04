# 云学堂网课自动观看工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> 自动观看网课视频工具，支持断点续看和后台播放。

## 特性

- ✅ **自动化**：自动登录、播放所有未完成课程
- ✅ **断点续看**：自动保存进度，随时中断继续
- ✅ **后台播放**：最小化浏览器不影响播放
- ✅ **模拟人类**：随机时长，模拟真实观看行为

## 快速开始

### 1. 安装依赖

**方式一：使用 uv（推荐）**
```bash
uv sync
```

**方式二：使用 pip**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**方式三：使用 conda**
```bash
conda create -n auto-watch python=3.10
conda activate auto-watch
pip install -r requirements.txt
```

### 2. 配置文件

**创建 `user.json`**
```bash
cp user.json.example user.json
```

编辑 `user.json`，填入登录信息：
```json
{
  "user_name": "你的学号或用户名",
  "password": "你的密码"
}
```

**编辑 `url.md`**
```
https://example.com/course/123
```

### 3. 运行程序

**使用 uv（推荐）**
```bash
uv run auto_watch
```

**使用 Python/Conda**
```bash
python main.py
```

## 使用说明

### 首次使用

1. 配置 `user.json` 和 `url.md`
2. 运行程序（选择一种方式）：
   - `uv run auto_watch`
   - `python main.py`
3. 程序会自动完成登录并开始观看

### 观看课程

- 程序自动播放所有未完成的课程
- 按 `Ctrl+C` 可随时安全中断
- 进度自动保存，下次运行继续

### 断点续看

- 进度保存在 `watch_progress.json`（自动生成）
- 删除该文件可重新开始

## 运行方式对比

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| **uv** | `uv run auto_watch` | 推荐使用，自动管理环境 |
| **Python** | `python main.py` | 使用 conda 或系统 Python |

**推荐 uv**：更快的依赖安装、更好的依赖解析、自动管理虚拟环境

## 配置文件说明

### user.json
用户登录信息，包含用户名和密码。已加入 `.gitignore`，不会被提交。

### url.md
网课的完整 URL 地址。

### watch_progress.json
自动生成的观看进度记录，包含：
- 当前观看的课程序号
- 已完成的课程列表
- 最后更新时间

## 注意事项

1. **环境要求**：确保已安装 Chrome 浏览器
2. **网络连接**：确保网络连接稳定
3. **电源设置**：确保电脑不会进入休眠模式
4. **数据安全**：登录信息保存在本地，请注意安全

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | Python 运行入口 |
| `auto_watch_courses/` | Python 包目录 |
| `auto_watch_courses/auto_watch.py` | 主程序逻辑 |
| `auto_watch_courses/login.py` | 登录功能 |
| `auto_watch_courses/watch_courses.py` | 观看课程功能 |
| `auto_watch_courses/selenium_server.py` | Selenium 控制服务器 |
| `auto_watch_courses/selenium_client.py` | 客户端调试工具 |
| `user.json` | 用户登录信息配置 |
| `url.md` | 网课网址配置 |
| `watch_progress.json` | 观看进度记录（自动生成） |
| `pyproject.toml` | 项目配置和依赖 |
| `requirements.txt` | 依赖列表 |

## 手动调试

使用 `selenium_client.py` 可以手动发送命令进行调试：

```bash
cd auto_watch_courses
python selenium_client.py info                # 获取页面信息
python selenium_client.py find ".h-login"    # 查找元素
python selenium_client.py click 0            # 点击元素
```

## 项目结构

```
Ten_Talks_on_New_Era_Workers/
├── auto_watch_courses/          # Python 包
│   ├── __init__.py
│   ├── auto_watch.py            # 主程序逻辑
│   ├── login.py                 # 登录功能
│   ├── watch_courses.py         # 观看课程功能
│   ├── selenium_server.py       # Selenium 服务器
│   └── selenium_client.py       # 客户端调试工具
├── main.py                      # Python 运行入口
├── pyproject.toml               # 项目配置
├── requirements.txt             # 依赖列表
├── user.json.example            # 配置示例
├── url.md                       # 网课网址
├── watch_progress.json          # 观看进度（自动生成）
├── .gitignore                   # Git 忽略文件
└── README.md
```

## LICENSE

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

**注意**：仅供学习研究使用，请勿用于商业用途。
