from ctypes import create_unicode_buffer
import ctypes
from ctypes import Structure, windll, c_uint, sizeof, byref, wintypes


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


def get_idle_duration() -> float:
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


def get_process_id_by_window_handle(handle):
    process_id = wintypes.DWORD()
    windll.user32.GetWindowThreadProcessId(handle, byref(process_id))
    return process_id


def get_process_name_by_pid(pid):
    max_path = 1024
    image_file_name = (ctypes.c_char * max_path)()
    process_query_information = 0x0400
    process_handle = ctypes.WinDLL('kernel32.dll').OpenProcess(process_query_information, False, pid)
    ctypes.WinDLL('Psapi.dll').GetProcessImageFileNameA(process_handle, image_file_name, max_path)
    image_file_name = image_file_name.value.decode()
    if not image_file_name:
        return 'Unknown'
    return image_file_name.split('\\')[-1]


def get_foreground_process_name_and_window_title():
    active_window = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(active_window)
    window_title = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(active_window, window_title, length + 1)

    process_id = get_process_id_by_window_handle(active_window)
    process_name = get_process_name_by_pid(process_id)

    window_title = window_title.value
    if not window_title:
        window_title = f'Unknown (process: {process_name})'
    return process_name, window_title
