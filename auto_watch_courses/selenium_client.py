"""
Selenium 服务器客户端
用于向服务器发送命令
"""
import requests
import json
import sys

SERVER_URL = "http://127.0.0.1:5000"

def send_command(endpoint, data=None):
    """发送命令到服务器"""
    url = f"{SERVER_URL}{endpoint}"
    try:
        if data:
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=10)

        result = response.json()
        return result
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器")
        print("请确保 selenium_server.py 正在运行")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def init_browser(url):
    """初始化浏览器"""
    return send_command('/init', {'url': url})

def execute_command(cmd, params=None):
    """执行命令"""
    data = {'cmd': cmd}
    if params:
        data['params'] = params
    return send_command('/execute', data)

def quit_browser():
    """关闭浏览器"""
    return send_command('/quit')

def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python selenium_client.py init <url>           - 初始化浏览器并访问URL")
        print("  python selenium_client.py find <selector>      - 查找元素")
        print("  python selenium_client.py click <index>        - 点击元素")
        print("  python selenium_client.py inputs               - 获取输入框")
        print("  python selenium_client.py buttons              - 获取按钮")
        print("  python selenium_client.py input <index> <text> - 输入文本")
        print("  python selenium_client.py screenshot           - 截图")
        print("  python selenium_client.py sleep <seconds>      - 等待")
        print("  python selenium_client.py html <index>         - 获取元素HTML")
        print("  python selenium_client.py js <javascript>      - 执行JS")
        print("  python selenium_client.py info                 - 获取页面信息")
        print("  python selenium_client.py text                 - 获取页面文本")
        print("  python selenium_client.py quit                 - 关闭浏览器")
        return

    command = sys.argv[1].lower()

    if command == 'init':
        if len(sys.argv) < 3:
            print("用法: python selenium_client.py init <url>")
            return
        url = sys.argv[2]
        result = init_browser(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'find':
        if len(sys.argv) < 3:
            print("用法: python selenium_client.py find <selector>")
            return
        selector = sys.argv[2]
        result = execute_command('find', {'selector': selector})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'click':
        if len(sys.argv) < 3:
            print("用法: python selenium_client.py click <index>")
            return
        index = int(sys.argv[2])
        result = execute_command('click', {'index': index})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'inputs':
        result = execute_command('inputs')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'buttons':
        result = execute_command('buttons')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'input':
        if len(sys.argv) < 4:
            print("用法: python selenium_client.py input <index> <text>")
            return
        index = int(sys.argv[2])
        text = sys.argv[3]
        result = execute_command('send_keys', {'index': index, 'text': text})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'screenshot':
        result = execute_command('screenshot')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'sleep':
        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        result = execute_command('sleep', {'seconds': seconds})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'html':
        if len(sys.argv) < 3:
            print("用法: python selenium_client.py html <index>")
            return
        index = int(sys.argv[2])
        result = execute_command('get_html', {'index': index})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'js':
        if len(sys.argv) < 3:
            print("用法: python selenium_client.py js <javascript>")
            return
        script = sys.argv[2]
        result = execute_command('execute_script', {'script': script})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'info':
        result = execute_command('page_info')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'text':
        result = execute_command('get_text')
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == 'quit':
        result = quit_browser()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")

if __name__ == '__main__':
    main()
