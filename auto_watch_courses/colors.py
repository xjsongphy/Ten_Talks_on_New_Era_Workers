"""
终端输出工具 - 无颜色版本
"""
from datetime import datetime

def get_timestamp():
    """获取时间戳"""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def print_header(text):
    """打印标题"""
    print(f"🏠 {text}")

def print_success(text):
    """打印成功信息"""
    print(f"✅ {get_timestamp()} {text}")

def print_error(text):
    """打印错误信息"""
    print(f"❌ {get_timestamp()} {text}")

def print_warning(text):
    """打印警告信息"""
    print(f"⚠️ {get_timestamp()} {text}")

def print_info(text):
    """打印信息"""
    print(f"ℹ️ {get_timestamp()} {text}")

def print_step(text):
    """打印步骤信息"""
    print(f"🔍 {get_timestamp()} {text}")

def print_label(text):
    """打印标签（不换行）"""
    print(f"🔍 {get_timestamp()} {text}", end="")

def print_banner(title, subtitle=""):
    """打印横幅"""
    if title:
        print(f"🏠 {title}")
    if subtitle:
        print(f"🏠 {subtitle}")
