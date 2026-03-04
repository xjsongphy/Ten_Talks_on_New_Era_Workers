"""
自动观看网课视频脚本 - 支持断点续看
"""
import json
import time
import os
from datetime import datetime, timedelta
import requests

SERVER_URL = "http://127.0.0.1:5000"
PROGRESS_FILE = "watch_progress.json"

# ANSI颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def format_time(seconds):
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}分{secs:02d}秒"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}小时{mins:02d}分{secs:02d}秒"

def progress_bar(current, total, width=30):
    """生成进度条"""
    if total == 0:
        return '█' * width
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    percentage = int(current / total * 100) if total > 0 else 0
    return f"{Colors.CYAN}[{bar}]{Colors.END} {percentage:>3}%"

class CourseWatcher:
    def __init__(self):
        self.progress = self.load_progress()
        self.video_start_time = None

    def load_progress(self):
        """加载观看进度"""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'current_course': 0,
            'completed_courses': [],
            'last_update': None
        }

    def save_progress(self):
        """保存观看进度（静默保存）"""
        self.progress['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def send_command(self, cmd, params=None):
        """发送命令到服务器"""
        data = {'cmd': cmd}
        if params:
            data['params'] = params
        try:
            response = requests.post(f"{SERVER_URL}/execute", json=data, timeout=30)
            result = response.json()
            if result.get('success') == False:
                print(f"[错误] {result.get('error')}")
                return None
            return result
        except Exception as e:
            print(f"[错误] 命令执行失败: {e}")
            return None

    def get_course_list(self):
        """获取课程列表"""
        print(f"\n{Colors.CYAN}📋 正在获取课程列表...{Colors.END}")

        # 点击课程目录标签
        result = self.send_command('execute_script', {
            'script': '''
                var tabs = document.querySelectorAll('.fwb_tab_item');
                if (tabs.length >= 2) {
                    tabs[1].click();
                    return 'Clicked catalog';
                }
                return 'Not found';
            '''
        })

        if not result:
            return []

        time.sleep(3)

        # 获取课程列表
        result = self.send_command('execute_script', {
            'script': '''
                var nodes = document.querySelectorAll('.el-tree-node .el-tree-node__content');
                var courses = [];
                for (var i = 0; i < nodes.length; i++) {
                    var text = nodes[i].innerText || '';
                    var match = text.match(/(\d{2}:\d{2}:\d{2})/);
                    if (match) {
                        var title = text.replace(match[0], '').trim();
                        courses.push({
                            index: courses.length,
                            title: title,
                            duration: match[0],
                            nodeIndex: i
                        });
                    }
                }
                return courses;
            '''
        })

        if not result:
            return []

        courses = result.get('data', {}).get('result', [])
        print(f"\n{Colors.GREEN}✓ 找到 {len(courses)} 个课程{Colors.END}\n")
        for i, course in enumerate(courses):
            if i < self.progress['current_course']:
                status = f"{Colors.GREEN}✓{Colors.END}"
                title = course.get('title', '')
            elif i == self.progress['current_course']:
                status = f"{Colors.YELLOW}▶{Colors.END}"
                title = f"{Colors.BOLD}{course.get('title', '')}{Colors.END}"
            else:
                status = " "
                title = course.get('title', '')
            duration = course.get('duration', '')
            print(f"  {status} {Colors.CYAN}{i+1:2d}.{Colors.END} {title} {Colors.BLUE}[{duration}]{Colors.END}")

        return courses

    def watch_video(self, course):
        """观看单个视频"""
        course_num = self.progress['current_course'] + 1
        print(f"\n{Colors.BOLD}{Colors.HEADER}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}║{Colors.END} {Colors.CYAN}开始观看第 {course_num}/10 讲{Colors.END} {Colors.BOLD}{Colors.HEADER}                              ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}╚════════════════════════════════════════════════════════════╝{Colors.END}")
        print(f"\n{Colors.BOLD}📺 {course.get('title', '')}{Colors.END}")
        print(f"⏱️  视频时长: {Colors.BLUE}{course.get('duration', '')}{Colors.END}")

        # 点击课程视频
        print(f"\n{Colors.YELLOW}⏳ 正在打开视频...{Colors.END}", flush=True)
        result = self.send_command('execute_script', {
            'script': f'''
                var nodes = document.querySelectorAll('.el-tree-node .el-tree-node__content');
                if (nodes[{course['nodeIndex']}]) {{
                    nodes[{course['nodeIndex']}].click();
                    return 'Clicked';
                }}
                return 'Not found';
            '''
        })

        if not result:
            print(f"{Colors.RED}✗ 点击视频失败{Colors.END}")
            return False

        time.sleep(3)

        # 切换到视频播放窗口
        result = self.send_command('switch_window', {'index': -1})

        if not result:
            print(f"{Colors.RED}✗ 切换窗口失败{Colors.END}")
            return False

        time.sleep(5)

        # 获取视频信息
        result = self.send_command('execute_script', {
            'script': '''
                var videos = document.querySelectorAll('video');
                if (videos.length > 0) {
                    return {
                        found: true,
                        duration: videos[0].duration,
                        currentTime: videos[0].currentTime,
                        paused: videos[0].paused
                    };
                }
                return {found: false};
            '''
        })

        if not result:
            print(f"{Colors.RED}✗ 获取视频信息失败{Colors.END}")
            return False

        video_info = result.get('data', {}).get('result', {})

        if not video_info.get('found'):
            print(f"{Colors.RED}✗ 未找到视频元素{Colors.END}")
            return False

        duration = video_info.get('duration', 0)
        print(f"{Colors.GREEN}✓ 视频已就绪{Colors.END} (总时长: {format_time(duration)})")

        # 开始播放视频（使用Selenium点击播放按钮，避免浏览器自动播放限制）
        if video_info.get('paused', True):
            # 先注入反后台暂停脚本
            self.send_command('execute_script', {
                'script': '''
                    Object.defineProperty(document, 'hidden', { get: () => false });
                    Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
                '''
            })
            # 用Selenium查找并点击播放按钮
            result = self.send_command('find', {'selector': '.xgplayer-start'})
            if result and result['data']['count'] > 0:
                self.send_command('click', {'index': 0})
            time.sleep(2)

        # 启动保持活跃的定时器
        self.send_command('execute_script', {
            'script': '''
                // 每5秒模拟一次用户活动
                window.keepActiveInterval = setInterval(function() {
                    // 模拟鼠标移动
                    window.dispatchEvent(new MouseEvent('mousemove', {
                        bubbles: true,
                        clientX: Math.random() * 100,
                        clientY: Math.random() * 100
                    }));

                    // 触发页面可见性检查
                    Object.defineProperty(document, 'hidden', { get: () => false });

                    // 检查视频是否暂停，如果是则点击播放按钮
                    var videos = document.querySelectorAll('video');
                    if (videos.length > 0 && videos[0].paused) {
                        console.log('Video was paused, clicking play button...');
                        var startBtn = document.querySelector('.xgplayer-start');
                        if (startBtn) {
                            startBtn.click();
                        }
                    }
                }, 5000);

                return 'Keep alive enabled';
            '''
        })

        # 模拟观看 - 定期检查进度
        self.video_start_time = time.time()
        elapsed = 0
        check_interval = 30  # 每30秒检查一次
        total_seconds = int(duration)

        print(f"\n{Colors.GREEN}▶️  开始播放...{Colors.END} {Colors.BLUE}(支持后台播放){Colors.END}\n")

        while elapsed < total_seconds:
            time.sleep(check_interval)
            elapsed += check_interval

            # 检查播放进度
            result = self.send_command('execute_script', {
                'script': '''
                    var videos = document.querySelectorAll('video');
                    if (videos.length > 0) {
                        return {
                            currentTime: videos[0].currentTime,
                            paused: videos[0].paused
                        };
                    }
                    return null;
                '''
            })

            if result:
                video_status = result.get('data', {}).get('result', {})
                if video_status:
                    current_time = int(video_status.get('currentTime', 0))
                    is_paused = video_status.get('paused', False)

                    # 如果视频暂停了，尝试继续播放
                    if is_paused:
                        # 使用Selenium点击播放按钮
                        result = self.send_command('find', {'selector': '.xgplayer-start'})
                        if result and result['data']['count'] > 0:
                            self.send_command('click', {'index': 0})

                    remaining = total_seconds - current_time
                    progress_pct = int((current_time / total_seconds) * 100)

                    # 计算预计剩余时间
                    elapsed_real = int(time.time() - self.video_start_time)
                    eta_seconds = int(remaining * elapsed_real / current_time) if current_time > 0 else 0

                    # 使用 \r 覆盖同一行，实现进度条动画效果
                    bar = progress_bar(current_time, total_seconds)
                    status_line = f"\r  {bar} │ {format_time(current_time)} / {format_time(total_seconds)} │ 剩余: {format_time(remaining)} │ ETA: {format_time(eta_seconds)}  "
                    print(status_line, end='', flush=True)

                    # 保存进度
                    self.save_progress()

                    # 检查是否播放完成
                    if remaining <= 5:
                        print(f"\n{Colors.GREEN}✓ 视频播放完成{Colors.END}")
                        break

        # 清理定时器和资源
        self.send_command('execute_script', {
            'script': '''
                // 清除保持活跃的定时器
                if (window.keepActiveInterval) {
                    clearInterval(window.keepActiveInterval);
                    window.keepActiveInterval = null;
                }
                return 'Cleaned up';
            '''
        })

        # 关闭视频窗口
        self.send_command('close_window', {})
        time.sleep(2)

        # 标记课程完成
        self.progress['current_course'] += 1
        course_id = f"course_{self.progress['current_course']}"
        if course_id not in self.progress['completed_courses']:
            self.progress['completed_courses'].append(course_id)

        self.save_progress()
        print(f"\n{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.END}")
        print(f"{Colors.GREEN}  ✓ 第 {course_num} 讲观看完成！{Colors.END}")
        print(f"{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.END}\n")

        return True

    def run(self):
        """主运行流程"""
        print(f"{Colors.BOLD}{Colors.HEADER}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}║{Colors.END} {Colors.CYAN}        自动观看网课脚本 - 支持断点续看{Colors.END}          {Colors.BOLD}{Colors.HEADER}║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}╚════════════════════════════════════════════════════════════╝{Colors.END}")
        print(f"{Colors.BLUE}🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")

        # 检查是否继续上次的进度
        start_course = self.progress['current_course']
        if start_course > 0:
            print(f"\n{Colors.YELLOW}📂 断点续看模式{Colors.END}")
            print(f"   从第 {Colors.CYAN}{start_course + 1}{Colors.END} 讲开始")
            print(f"   已完成: {Colors.GREEN}{len(self.progress.get('completed_courses', []))}{Colors.END} 讲")

        try:
            # 获取课程列表
            courses = self.get_course_list()

            if not courses:
                print(f"{Colors.RED}[错误] 未获取到课程列表{Colors.END}")
                return

            # 从当前进度开始观看
            for i in range(start_course, len(courses)):
                success = self.watch_video(courses[i])

                if not success:
                    print(f"{Colors.RED}[错误] 第 {i+1} 讲观看失败{Colors.END}")
                    break

                # 观看完成后等待一段时间再继续下一讲
                if i < len(courses) - 1:
                    print(f"{Colors.YELLOW}⏳ 5秒后继续下一讲...{Colors.END}\n")
                    time.sleep(5)

            # 检查是否全部完成
            if self.progress['current_course'] >= len(courses):
                print(f"\n{Colors.GREEN}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.END}")
                print(f"{Colors.GREEN}{Colors.BOLD}║{Colors.END}           🎉 全部课程观看完成！🎉            {Colors.GREEN}{Colors.BOLD}║{Colors.END}")
                print(f"{Colors.GREEN}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.END}")
                print(f"{Colors.BLUE}🕐 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
                print(f"{Colors.GREEN}✓ 完成课程数: {len(self.progress.get('completed_courses', []))} / 10{Colors.END}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}[中断] 用户手动中断{Colors.END}")
            print(f"{Colors.BLUE}💾 进度已保存，下次可以继续{Colors.END}")
            self.save_progress()
        except Exception as e:
            print(f"\n{Colors.RED}[错误] 发生异常: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            self.save_progress()

if __name__ == '__main__':
    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    print(f"{Colors.BOLD}  使用说明{Colors.END}")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    print(f"  1️⃣  确保已经运行 {Colors.YELLOW}login.py{Colors.END} 完成登录")
    print(f"  2️⃣  确保服务器正在运行 ({Colors.YELLOW}python selenium_server.py{Colors.END})")
    print(f"  3️⃣  运行此脚本开始自动观看")
    print(f"  4️⃣  按 {Colors.YELLOW}Ctrl+C{Colors.END} 可以随时中断，进度会自动保存")
    print(f"  5️⃣  下次运行会自动从上次的位置继续")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}\n")

    watcher = CourseWatcher()
    watcher.run()
