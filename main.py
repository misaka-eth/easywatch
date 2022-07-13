import time
from helpers import get_foreground_process_name_and_window_title, get_idle_duration
from prometheus_client import Gauge, start_http_server


def main():
    try:
        start_http_server(8889)
        active_window = Gauge('active_window', 'Active window info', ['name', 'title', 'afk'])
        afk = Gauge('afk', 'Time since last activity')

        last_active_process_name, last_active_window_name, last_afk = None, None, None
        while True:
            active_process_name, active_window_name = get_foreground_process_name_and_window_title()
            afk_time = get_idle_duration()
            is_afk = afk_time > 60

            is_new_process_name = last_active_process_name != active_process_name
            is_new_window_name = last_active_window_name != active_window_name
            is_new_afk = last_afk != is_afk
            is_new_window = is_new_process_name or is_new_window_name

            if last_active_process_name and (is_new_window or is_new_afk):
                active_window.clear()

            active_window.labels(name=active_process_name, title=active_window_name, afk=is_afk).set(1)
            afk.set(afk_time)

            last_active_process_name, last_active_window_name = active_process_name, active_window_name
            last_afk = is_afk

            time.sleep(1)

    except Exception as error:
        print(f"Stopped due to error: {error.__class__}({error})")


if __name__ == '__main__':
    main()
