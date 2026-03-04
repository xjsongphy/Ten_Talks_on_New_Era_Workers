"""
Selenium 控制服务器
在本地运行此服务器，然后发送HTTP请求来控制浏览器
"""
import json
import time
import os
from datetime import datetime
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
app = Flask(__name__)

# 全局浏览器实例
driver = None
last_found_elements = []

# 日志文件
LOG_FILE = "server_log.txt"
HTML_LOG_FILE = "page_html.txt"

def log(msg, also_print=True):
    """写入日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')
    if also_print:
        print(log_msg)

def save_page_html():
    """保存当前页面HTML"""
    if driver:
        with open(HTML_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        log(f"页面HTML已保存到 {HTML_LOG_FILE}", also_print=False)

def init_browser():
    """初始化浏览器"""
    global driver
    if driver is None:
        log("正在初始化浏览器...")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        # 添加反后台检测参数
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-renderer')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)

        # 注入反后台暂停的脚本到所有新页面
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // 反后台暂停脚本
                (function() {
                    // 覆盖 Page Visibility API
                    Object.defineProperty(document, 'hidden', { get: () => false });
                    Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
                    Object.defineProperty(document, 'webkitHidden', { get: () => false });
                    Object.defineProperty(document, 'webkitVisibilityState', { get: () => 'visible' });

                    // 拦截 visibilitychange 事件
                    document.addEventListener('visibilitychange', function(e) {
                        e.stopImmediatePropagation();
                    }, true);

                    // 定期触发焦点事件
                    setInterval(function() {
                        window.dispatchEvent(new Event('focus'));
                    }, 1000);
                })();
            '''
        })

        log("浏览器初始化完成 (已启用反后台暂停)")
    return driver

@app.route('/status', methods=['GET'])
def status():
    """获取服务器状态"""
    return jsonify({
        'status': 'running',
        'browser_active': driver is not None,
        'current_url': driver.current_url if driver else None
    })

@app.route('/init', methods=['POST'])
def init():
    """初始化浏览器并访问URL"""
    try:
        data = request.json
        url = data.get('url')

        driver = init_browser()

        if url:
            log(f"正在访问URL: {url}")
            driver.get(url)
            time.sleep(3)
            save_page_html()

        return jsonify({
            'success': True,
            'current_url': driver.current_url,
            'title': driver.title
        })
    except Exception as e:
        log(f"初始化失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/execute', methods=['POST'])
def execute():
    """执行命令"""
    global last_found_elements

    try:
        data = request.json
        cmd = data.get('cmd', '')
        params = data.get('params', {})

        log(f"执行命令: {cmd}")

        result = {'success': True, 'data': None}

        if cmd == 'find':
            # 查找元素
            selector = params.get('selector')
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log(f"找到 {len(elements)} 个元素 (选择器: {selector})")

            last_found_elements = []
            elem_list = []
            for i, elem in enumerate(elements[:50]):  # 限制50个
                tag = elem.tag_name
                text = (elem.text or '')[:100]
                class_attr = elem.get_attribute('class') or ''
                id_attr = elem.get_attribute('id') or ''
                elem_info = {
                    'index': i,
                    'tag': tag,
                    'text': text,
                    'class': class_attr,
                    'id': id_attr
                }
                elem_list.append(elem_info)
                last_found_elements.append(elem)

            result['data'] = {
                'count': len(elements),
                'elements': elem_list
            }

        elif cmd == 'click':
            # 点击元素
            index = params.get('index', 0)
            if 0 <= index < len(last_found_elements):
                elem = last_found_elements[index]
                log(f"点击元素 [{index}]")
                elem.click()
                time.sleep(2)
                save_page_html()
                result['data'] = {
                    'current_url': driver.current_url
                }
            else:
                raise Exception(f"索引 {index} 超出范围")

        elif cmd == 'inputs':
            # 获取所有输入框
            inputs = driver.find_elements(By.TAG_NAME, "input")
            log(f"找到 {len(inputs)} 个输入框")

            input_list = []
            last_found_elements = []
            for i, inp in enumerate(inputs):
                info = {
                    'index': i,
                    'type': inp.get_attribute('type'),
                    'name': inp.get_attribute('name'),
                    'placeholder': inp.get_attribute('placeholder'),
                    'class': inp.get_attribute('class'),
                    'id': inp.get_attribute('id')
                }
                input_list.append(info)
                last_found_elements.append(inp)

            result['data'] = {
                'count': len(inputs),
                'inputs': input_list
            }

        elif cmd == 'buttons':
            # 获取所有按钮
            buttons = driver.find_elements(By.TAG_NAME, "button")
            log(f"找到 {len(buttons)} 个按钮")

            btn_list = []
            last_found_elements = []
            for i, btn in enumerate(buttons):
                info = {
                    'index': i,
                    'text': btn.text.strip(),
                    'class': btn.get_attribute('class'),
                    'id': btn.get_attribute('id')
                }
                btn_list.append(info)
                last_found_elements.append(btn)

            result['data'] = {
                'count': len(buttons),
                'buttons': btn_list
            }

        elif cmd == 'send_keys':
            # 向输入框发送文本
            index = params.get('index', 0)
            text = params.get('text', '')

            if 0 <= index < len(last_found_elements):
                elem = last_found_elements[index]
                log(f"向元素 [{index}] 输入: {text}")
                elem.clear()
                elem.send_keys(text)
                time.sleep(0.5)
                result['data'] = {'success': True}
            else:
                raise Exception(f"索引 {index} 超出范围")

        elif cmd == 'screenshot':
            # 截图
            filename = params.get('filename', f"screenshot_{int(time.time())}.png")
            driver.save_screenshot(filename)
            log(f"截图已保存: {filename}")
            result['data'] = {'filename': filename}

        elif cmd == 'execute_script':
            # 执行JavaScript
            script = params.get('script')
            log(f"执行JS: {script[:100]}...")
            script_result = driver.execute_script(script)
            log(f"JS结果: {script_result}")
            result['data'] = {'result': script_result}

        elif cmd == 'get_html':
            # 获取元素HTML
            index = params.get('index', 0)
            if 0 <= index < len(last_found_elements):
                elem = last_found_elements[index]
                html = elem.get_attribute('innerHTML')
                log(f"元素 [{index}] HTML长度: {len(html)}")
                result['data'] = {'html': html[:5000]}  # 限制大小
            else:
                raise Exception(f"索引 {index} 超出范围")

        elif cmd == 'sleep':
            # 等待
            seconds = params.get('seconds', 5)
            log(f"等待 {seconds} 秒...")
            time.sleep(seconds)
            save_page_html()
            result['data'] = {'slept': seconds}

        elif cmd == 'get_text':
            # 获取页面文本
            text = driver.find_element(By.TAG_NAME, "body").text
            result['data'] = {'text': text[:2000]}

        elif cmd == 'page_info':
            # 获取页面信息
            result['data'] = {
                'url': driver.current_url,
                'title': driver.title,
                'source_length': len(driver.page_source)
            }

        elif cmd == 'switch_window':
            # 切换到新窗口
            window_index = params.get('index', -1)  # -1 表示最新窗口
            handles = driver.window_handles
            log(f"当前有 {len(handles)} 个窗口")

            if window_index == -1:
                # 切换到最新窗口
                driver.switch_to.window(handles[-1])
                log(f"切换到最新窗口")
            elif 0 <= window_index < len(handles):
                driver.switch_to.window(handles[window_index])
                log(f"切换到窗口 {window_index}")
            else:
                raise Exception(f"窗口索引 {window_index} 超出范围")

            save_page_html()
            result['data'] = {
                'current_url': driver.current_url,
                'title': driver.title,
                'window_count': len(handles)
            }

        elif cmd == 'close_window':
            # 关闭当前窗口并切换回主窗口
            driver.close()
            handles = driver.window_handles
            if handles:
                driver.switch_to.window(handles[0])
                log("关闭当前窗口，切换回主窗口")
            save_page_html()
            result['data'] = {
                'current_url': driver.current_url,
                'title': driver.title
            }

        else:
            raise Exception(f"未知命令: {cmd}")

        return jsonify(result)

    except Exception as e:
        error_msg = f"执行失败: {e}"
        log(error_msg)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/quit', methods=['POST'])
def quit():
    """关闭浏览器"""
    global driver
    if driver:
        driver.quit()
        driver = None
        log("浏览器已关闭")
    return jsonify({'success': True})

if __name__ == '__main__':
    # 清空日志文件
    open(LOG_FILE, 'w').close()
    log("Selenium控制服务器启动")
    log("访问 http://localhost:5000 来控制浏览器")
    log("可用端点: /status, /init, /execute, /quit")

    app.run(host='127.0.0.1', port=5000, debug=False)
