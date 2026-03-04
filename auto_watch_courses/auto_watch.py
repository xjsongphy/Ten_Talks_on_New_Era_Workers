"""
网课自动观看主脚本
整合登录和观看功能，支持断点续看
"""
import os
import sys
import time
import subprocess

from . import login
from . import watch_courses
from . import colors

def check_server_running():
    """检查服务器是否运行"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:5000/status', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """启动Selenium服务器"""
    server_script = os.path.join(os.path.dirname(__file__), 'selenium_server.py')
    subprocess.Popen(
        [sys.executable, server_script],
        cwd=os.getcwd(),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    colors.print_info("服务器正在启动，请等待5秒...")
    time.sleep(5)

    if check_server_running():
        colors.print_success("服务器启动成功")
        return True
    else:
        colors.print_error("✗ 服务器启动失败")
        return False

def main():
    colors.print_info("云学堂网课自动观看工具")
    colors.print_info("支持断点续看 | 自动登录 | 模拟人类行为")

    if not check_server_running():
        colors.print_info("服务器未运行，正在启动...")
        if not start_server():
            colors.print_error("错误: 无法启动服务器")
            print("请手动运行: python selenium_server.py")
            return
    else:
        colors.print_success("服务器运行中")

    colors.print_info("开始登录流程...")
    success = login.do_login()
    if not success:
        colors.print_error("登录失败，请检查用户名和密码")
        return
    colors.print_success("登录成功！")

    colors.print_info("开始自动观看课程...")
    watcher = watch_courses.CourseWatcher()
    watcher.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序结束")
