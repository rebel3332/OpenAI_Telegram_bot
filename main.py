import os
import requests
from PIL import Image
import time

from Telegram import Telegram
from Parametrs import Parametrs
from BD import BD

if __name__=='__main__':
    print(f'Telegram Bot has started!')
    # global SQL
    SQL = BD()
    parametrs = Parametrs(BD=SQL)
    count = 0
    # if True:
    while True:
        try:
            Tele = Telegram(parametrs, BD=SQL)
            Tele.run()
        except Exception as e:
            count += 1
            SQL.put_log_worksteps(f'Ошибка №{count}: {e}', event_type='main while')
            time.sleep(3)
