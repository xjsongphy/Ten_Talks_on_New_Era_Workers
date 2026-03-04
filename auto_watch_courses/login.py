"""
网课登录脚本
自动完成云学堂平台的登录流程
"""
import requests
import time
import json

from . import colors

SERVER_URL = "http://127.0.0.1:5000"

def send_command(cmd, params=None):
    """发送命令到服务器"""
    data = {'cmd': cmd}
    if params:
        data['params'] = params
    try:
        response = requests.post(f"{SERVER_URL}/execute", json=data, timeout=30)
        return response.json()
    except Exception as e:
        colors.print_error(f"[错误] 命令执行失败: {e}")
        return None

def load_user_info():
    """加载用户信息"""
    with open('user.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_url():
    """加载网址"""
    with open('url.md', 'r', encoding='utf-8') as f:
        return f.read().strip()

def do_login():
    """执行登录流程"""
    print("=" * 60)
    print("    云学堂网课自动登录")
    print("=" * 60)
    user_info = load_user_info()
    course_url = load_url()

    colors.print_step("访问网课页面")
    result = requests.post(f"{SERVER_URL}/init", json={'url': course_url}, timeout=30).json()
    if not result.get('success'):
        colors.print_error("✗ 初始化失败")
        return False
    colors.print_success("页面已加载")

    colors.print_step("点击登录按钮")
    result = send_command('find', {'selector': '.h-login'})
    if result and result['data']['count'] > 0:
        send_command('click', {'index': 0})
        colors.print_success("登录按钮已点击")
        time.sleep(2)
    else:
        colors.print_error("✗ 未找到登录按钮")
        return False

    colors.print_step("点击统一身份认证（第一次）")
    result = send_command('execute_script', {
        'script': '''
            var authText = document.querySelector('.denglu_text_one');
            if (authText) {
                authText.click();
                return 'Clicked unified auth (1st)';
            }
            return 'Not found';
        '''
    })
    print(f"  状态: {result.get('data', {}).get('result', 'Unknown')}")
    time.sleep(2)

    colors.print_step("点击同意并继续")
    result = send_command('execute_script', {
        'script': '''
            return new Promise(function(resolve) {
                setTimeout(function() {
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].innerText || buttons[i].textContent || '';
                        if (text.indexOf('同意并继续') > -1) {
                            buttons[i].click();
                            resolve('Clicked button');
                            return;
                        }
                    }
                    resolve('Button not found');
                }, 1000);
            });
        '''
    })
    print(f"  状态: {result.get('data', {}).get('result', 'Unknown')}")
    time.sleep(2)

    colors.print_step("再次点击统一身份认证")
    result = send_command('execute_script', {
        'script': '''
            var authText = document.querySelector('.denglu_text_one');
            if (authText) {
                authText.click();
                return 'Clicked unified auth (2nd)';
            }
            return 'Not found';
        '''
    })
    print(f"  状态: {result.get('data', {}).get('result', 'Unknown')}")
    time.sleep(5)

    colors.print_step("输入用户名")
    result = send_command('find', {'selector': '#user_name'})
    if result and result['data']['count'] > 0:
        send_command('send_keys', {'index': 0, 'text': user_info['user_name']})
        colors.print_success(f"用户名: {user_info['user_name']}")
        time.sleep(0.5)
    else:
        colors.print_error("✗ 未找到用户名输入框")
        return False

    colors.print_step("输入密码")
    result = send_command('find', {'selector': '#password'})
    if result and result['data']['count'] > 0:
        send_command('send_keys', {'index': 0, 'text': user_info['password']})
        colors.print_success(f"密码: {'*' * len(user_info['password'])}")
        time.sleep(0.5)
    else:
        colors.print_error("✗ 未找到密码输入框")
        return False

    colors.print_step("点击登录按钮")
    result = send_command('find', {'selector': '#logon_button'})
    if result and result['data']['count'] > 0:
        send_command('click', {'index': 0})
        colors.print_success("登录按钮已点击")
    else:
        colors.print_error("✗ 未找到登录按钮")
        return False

    colors.print_info("正在跳转回网课页面...")
    time.sleep(5)

    result = send_command('page_info', {})
    current_url = result.get('data', {}).get('url', '')

    if 'byyxt.pupedu.cn' in current_url:
        print()
        colors.print_success("登录成功！")
        print(f"  当前页面: {current_url}")
        return True
    else:
        colors.print_error(f"✗ 登录可能失败，当前URL: {current_url}")
        return False

if __name__ == '__main__':
    try:
        success = do_login()
        if success:
            print("\n登录完成，可以继续其他操作")
        else:
            print("\n登录失败，请检查")
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
