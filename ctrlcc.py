import os
import sys
import pyperclip
import keyboard
from threading import Timer
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw
from ctypes import windll
import winreg as reg
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
import logging
import subprocess
import re


def get_log_file_path():
    """Get the path for the log file, differentiating between script and executable."""
    if getattr(sys, 'frozen', False):
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, 'ctrlcc')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(log_dir, 'CtrlC_C_log.txt')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CtrlC_C_log.txt')


def view_logs(icon, item):
    """Open the log file with the default text editor."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(log_filepath)
        elif os.name == 'posix':  # Unix-like
            subprocess.run(['open', log_filepath], check=True)
        else:
            logging.error("Unsupported OS for viewing logs")
    except Exception as e:
        logging.error(f"Error opening log file: {e}")


def add_to_startup():
    """Add the application to the Windows startup registry."""
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = os.path.abspath(__file__)

    try:
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open, "CtrlC+C", 0, reg.REG_SZ, app_path)
        reg.CloseKey(open)
        return True
    except WindowsError:
        return False


def remove_from_startup():
    """Remove the application from the Windows startup registry."""
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(open, "CtrlC+C")
        reg.CloseKey(open)
        return True
    except WindowsError:
        return False


def toggle_startup():
    """Toggle whether the application is in the Windows startup registry."""
    if is_in_startup():
        return remove_from_startup()
    else:
        return add_to_startup()


def is_in_startup():
    """Check whether the application is in the Windows startup registry."""
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        open = reg.OpenKey(key, key_value, 0, reg.KEY_READ)
        reg.QueryValueEx(open, "CtrlC+C")
        reg.CloseKey(open)
        return True
    except WindowsError:
        return False


def show_message_box(title, message):
    """Show a message box with the given title and message."""
    return windll.user32.MessageBoxW(0, message, title, 0)


def toggle_strip_blankspace():
    """Toggle whether to remove blank space from copied text."""
    global is_strip_blankspace
    is_strip_blankspace = not is_strip_blankspace
    return is_strip_blankspace


def toggle_smart_newlines():
    """Toggle whether to use smart newline processing."""
    global is_smart_newlines
    is_smart_newlines = not is_smart_newlines
    return is_smart_newlines


def strip_newlines(text):
    """Remove all types of newline characters from a string."""
    try:
        text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        logging.info(f"removed newlines: {text}")  # Log the stripped text
        return text
    except Exception as e:
        logging.error(f"Error while accessing clipboard: {e}")
        return ""


def smart_strip_newlines(text):
    """智能处理换行符，保留段落间的换行，去除行内换行。
    
    通过以下规则识别段落换行：
    1. 连续的两个或以上的换行符视为段落分隔
    2. 以句号、问号、感叹号等结尾的行后的换行视为段落分隔
    3. 其他情况的单个换行符视为PDF复制产生的行内换行，替换为空格
    """
    try:
        # 标准化所有换行符为 \n
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 处理连续的换行符（规则1：连续换行符保留为段落分隔）
        text = re.sub(r'\n{2,}', '\n\n', text)
        
        # 处理句子结束后的换行（规则2：句末换行视为段落分隔）
        # 英文标点
        text = re.sub(r'([.!?:;"\'])[ \t]*\n', r'\1\n\n', text)
        # 中文标点
        text = re.sub(r'([。！？；：])[ \t]*\n', r'\1\n\n', text)
        # 中文引号
        text = re.sub(r'([""])[ \t]*\n', r'\1\n\n', text)
        # 括号
        text = re.sub(r'([)）》>])[ \t]*\n', r'\1\n\n', text)
        # 省略号
        text = re.sub(r'(…)[ \t]*\n', r'\1\n\n', text)
        
        # 处理其他单个换行符（规则3：其他换行替换为空格）
        text = re.sub(r'(?<!\n)[ \t]*\n(?!\n)', ' ', text)
        
        # 清理连续的多个空格
        text = re.sub(r' {2,}', ' ', text)
        
        # 确保段落之间只有一个空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        logging.info(f"智能处理换行: {text}")
        return text
    except Exception as e:
        logging.error(f"Error while processing newlines: {e}")
        return text


def strip_blankspace(text):
    """Remove all types of blank space characters from a string."""
    try:
        text = text.replace(' ', '')
        logging.info(f"removed blank space: {text}")  # Log the stripped text
        return text
    except Exception as e:
        logging.error(f"Error while accessing clipboard: {e}")
        return ""


def get_clipboard_text():
    """Get the current text on the clipboard and then clear it."""
    try:
        text = pyperclip.paste()
        pyperclip.copy("")  # Clear the clipboard
        return text
    except Exception as e:
        logging.error(f"Error while accessing clipboard: {e}")
        return ""


def set_clipboard_text(text):
    """Set the given text on the clipboard."""
    pyperclip.copy(text)


def on_c_press(event):
    global strip_attempted
    """Start a timer after first 'C' press, if 'Ctrl' is held down"""
    if keyboard.is_pressed('ctrl'):
        if hasattr(on_c_press, 'first_press_timer') and on_c_press.first_press_timer is not None:
            # If timer exists, we are within 1.0 seconds of first press, so we execute the action
            on_c_press.first_press_timer.cancel()
            strip_attempted = True
            perform_clipboard_action()
            Timer(0.5, check_conflict).start()
        else:
            # Start a timer that waits for another 'C' press within 1.0 seconds
            on_c_press.first_press_timer = Timer(1.0, reset_first_press_timer)
            on_c_press.first_press_timer.start()
    else:
        reset_first_press_timer()


def check_conflict():
    """Check if strip_newlines was attempted but not executed, indicating a hotkey conflict."""
    global strip_attempted, strip_executed
    if strip_attempted and not strip_executed:
        # If strip_newlines was attempted but not executed, then we might have a conflict
        show_message_box("快捷键冲突", "Ctrl+C+C 快捷键可能被其他程序占用。")
    # Reset flags for the next attempt
    strip_attempted = False
    strip_executed = False


def perform_clipboard_action():
    """Perform the action of copying the clipboard text and removing newlines."""
    global strip_executed
    reset_first_press_timer()
    try:
        current_data = get_clipboard_text()
        
        # 根据设置选择换行处理方式
        if is_smart_newlines:
            stripped_text = smart_strip_newlines(current_data)
        else:
            stripped_text = strip_newlines(current_data)
            
        if is_strip_blankspace:
            stripped_text = strip_blankspace(stripped_text)
        set_clipboard_text(stripped_text)
        logging.info(f"Stripped text: {stripped_text}")
        strip_executed = True
    except Exception as e:
        logging.error(f"Error in perform_clipboard_action: {e}")


def reset_first_press_timer():
    """Reset the timer for double 'C' press"""
    on_c_press.first_press_timer = None


def create_icon(image_name):
    """获取图标文件的路径"""
    try:
        # 检查应用是否被打包
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            base_path = sys._MEIPASS
        else:
            # 如果是直接运行的脚本
            base_path = os.path.abspath(os.path.dirname(__file__))

        # 构建图标文件的完整路径
        icon_path = os.path.join(base_path, image_name)
        logging.info(f"尝试加载图标: {icon_path}")
        
        # 检查文件是否存在
        if not os.path.exists(icon_path):
            logging.error(f"图标文件不存在: {icon_path}")
            # 创建一个默认的空白图标
            img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((10, 10, 54, 54), fill=(66, 133, 244))
            draw.text((27, 27), "C+C", fill=(255, 255, 255))
            return img
        
        return Image.open(icon_path)
    except Exception as e:
        logging.error(f"加载图标失败: {e}")
        # 创建一个默认的空白图标
        img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((10, 10, 54, 54), fill=(66, 133, 244))
        draw.text((27, 27), "C+C", fill=(255, 255, 255))
        return img


def setup_tray_icon():
    """Load your own image as icon and setup tray icon with menu"""
    icon_image = create_icon("ctrlcc.ico")

    # The menu that will appear when the user right-clicks the icon
    menu = (item('开机自启', toggle_startup, checked=lambda item: is_in_startup()),
            item('智能换行处理', toggle_smart_newlines, checked=lambda item: is_smart_newlines),
            item('去除空格', toggle_strip_blankspace, checked=lambda item: is_strip_blankspace),
            item('查看日志', view_logs),
            item('退出', exit_program),)
    icon = pystray.Icon("test_icon", icon_image, "CtrlC+C", menu)
    icon.run()


def exit_program(icon, item):
    """Exit the program and stop the system tray icon"""
    icon.stop()  # This will stop the system tray icon and the associated message loop.
    keyboard.unhook_all()
    # print("Exiting program...")


if __name__ == "__main__":

    log_filepath = get_log_file_path()
    logging.basicConfig(filename=log_filepath, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    strip_attempted = False
    strip_executed = False

    is_strip_blankspace = False
    is_smart_newlines = True  # 默认启用智能换行处理

    mutex_name = "CtrlC_C_Application_Mutex"

    mutex = win32event.CreateMutex(None, False, mutex_name)
    last_error = win32api.GetLastError()

    if last_error == ERROR_ALREADY_EXISTS:
        show_message_box("应用程序已运行", "CtrlC+C 应用程序已经在运行了。")
        sys.exit(0)

    # Show instruction message box
    instruction_message = (
        "欢迎使用 CtrlC+C ！\n"
        "\n"
        "【按住 Ctrl 键并按 C 键两次】以复制文本并智能处理换行。\n"
        "\n"
        "功能说明：\n"
        "1. 智能换行处理：\n"
        "   - 保留段落之间的换行\n"
        "   - 保留句子末尾（标点符号后）的换行\n"
        "   - 去除PDF复制产生的行内换行\n"
        "2. 可在系统托盘图标右键菜单中切换功能选项\n"
        "3. 支持开机自启动\n"
        "\n"
        "如有问题，请联系：chenluda01@gmail.com"
    )
    show_message_box("© 2023 Glenn.", instruction_message)

    # Initialization and event hooks
    # print("Hold Ctrl and press C twice to copy text and remove newlines...")
    # print("Press Esc to quit.")
    on_c_press.first_press_timer = None
    keyboard.on_release_key('c', on_c_press)
    # keyboard.add_hotkey('esc', lambda: exit_program(None, None))  # Adapted for direct call
    setup_tray_icon()  # Start the system tray icon
