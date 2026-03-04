"""
网课自动观看主脚本
整合登录和观看功能，支持断点续看
"""
import os
import sys
import subprocess

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
    print("[启动] Selenium服务器...")
    # 使用子进程启动服务器，不阻塞
    subprocess.Popen(
        ['C:\\Users\\xjsongphy\\miniconda3\\envs\\aw\\python.exe', 'selenium_server.py'],
        cwd=os.getcwd(),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("服务器正在启动，请等待5秒...")
    import time
    time.sleep(5)

    if check_server_running():
        print("✓ 服务器启动成功")
        return True
    else:
        print("✗ 服务器启动失败")
        return False

def main():
    print("="*70)
    print("    云学堂网课自动观看工具")
    print("    支持断点续看 | 自动登录 | 模拟人类行为")
    print("="*70)

    # 检查服务器
    if not check_server_running():
        print("\n服务器未运行，正在启动...")
        if not start_server():
            print("\n错误: 无法启动服务器")
            print("请手动运行: python selenium_server.py")
            return
    else:
        print("\n✓ 服务器运行中")

    # # 询问用户是否需要登录
    # print("\n请选择操作:")
    # print("1. 登录 (首次使用或登录过期)")
    # print("2. 开始观看 (已登录)")

    # while True:
    #     choice = input("\n请输入选项 (1/2): ").strip()
    #     if choice in ['1', '2']:
    #         break
    #     print("无效选项，请重新输入")

    # if choice == '1':

    # 执行登录
    print("\n开始登录流程...")
    import login
    success = login.do_login()
    if not success:
        print("\n登录失败，请检查用户名和密码")
        return
    print("\n登录成功！")

    # # 询问是否立即开始观看
    # start_now = input("\n是否立即开始观看? (y/n): ").strip().lower()
    # if start_now != 'y':
    #     print("\n已登录，稍后可以运行此脚本选择选项2开始观看")
    #     return

    # 执行观看
    print("\n开始自动观看课程...")
    import watch_courses
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
