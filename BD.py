import sqlite3
from datetime import datetime
import ast


class BD:
    """
    Класс позволяет читать историю переписки и сохранять новые сообщения в БД
    """
    def __init__(self) -> None:
        self.sql_base = 'chat_gpt3.5_turbo.db'
        self.con = sqlite3.connect(self.sql_base, check_same_thread=False)
        self.put_log_worksteps('SQL инициализирован', event_type='program')

    def get_messages(self, channel_id):
        """ 
        Получает историю переписки из базы \n
        SELECT id_messages, role, text FROM messages ORDER BY id_messages ASC
        """

        self.cur = self.con.cursor()
        self.cur.execute(f"""
                             select  id_messages, role, text 
                             from messages as m 
                             where 
                                m.id_messages in (select id_messages from messages where channel_id = '{channel_id}' 
                                and m.role <> 'Error'
                             order by id_messages DESC limit 10) ORDER BY id_messages ASC""")
        # self.cur.execute(f"SELECT id_messages, role, text FROM messages WHERE channel_id = '{channel_id}' ORDER BY id_messages ASC")
        mess = []
        for row in self.cur.fetchall():
            mess.append({"role": row[1], "content": row[2]})
        self.cur.close()
        return mess
    
    def put_message(self, role, text, messenger, user_id, user_name, channel_id, channel_url, insert_date):
        """ 
        Записыва сообщение в базу\n
        INSERT INTO messages(role, text) values('{role}', '{text}', '{messenger}', '{user_id}', '{user_name}', '{channel_id}', '{channel_url}', '{insert_date}')
        """
        text = text.replace("'",'"').replace('/n/n','').replace('  ',' ')
        self.cur = self.con.cursor()
        self.cur.execute(f"INSERT INTO messages(role, text, messenger, user_id, user_name, channel_id, chanal_url, insert_date) values('{role}', '{text}', '{messenger}', '{user_id}', '{user_name}', '{channel_id}', '{channel_url}', '{insert_date}')")
        self.con.commit()
        self.cur.close()

    def put_access(self, acces_date, user_id, user_name, messenger, channel_id, chanal_url, success):
        """ 
	"acces_date"	TEXT,
	"user_id"	TEXT,
	"user_name"	TEXT,
	"messenger"	TEXT,
	"channel_id"	TEXT,
	"chanal_url"	TEXT,
	"success"	BLOB,
        Записыва сообщение в базу\n
        INSERT INTO messages(role, text) values('{role}', '{text}', '{messenger}', '{user_id}', '{user_name}', '{channel_id}', '{channel_url}', '{insert_date}')
        """
        messenger = messenger.replace("'",'"').replace('/n/n','').replace('  ',' ')
        self.cur = self.con.cursor()
        self.cur.execute(f"INSERT INTO access(acces_date, user_id, user_name, messenger, channel_id, chanal_url, success) values('{acces_date}', '{user_id}', '{user_name}', '{messenger}', '{channel_id}', '{chanal_url}', '{success}')")
        self.con.commit()
        self.cur.close()


    def get_channel_statistic(self, channel_id, role = ''):
        """ 
        Получает статистику по сообщениям в канале из базы \n
        SELECT id_messages, role, text FROM messages ORDER BY id_messages ASC
        """

        self.cur = self.con.cursor()
        if role == '':
            self.cur.execute(f"""
                                select count(*) as cnt, min(insert_date) as first_date, max(insert_date) as last_date
                                from messages
                                where channel_id = '{channel_id}'
                                group by channel_id""")
        else:
            self.cur.execute(f"""
                                select count(*) as cnt, min(insert_date) as first_date, max(insert_date) as last_date
                                from messages
                                where channel_id = '{channel_id}' and role = '{role}'
                                group by channel_id""")
        for row in self.cur.fetchall():
            mess = row
        self.cur.close()
        return row


    def put_log_worksteps(self, text, event_type=''):
        """ 
        "type" TEXT,
	    "text"	TEXT,
        Записыва сообщение в базу\n
        INSERT INTO log_worksteps(date, type, text) values('{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}', '{event_type}', '{text}')
        """
        text = text.replace("'",'"').replace('/n/n','').replace('  ',' ')
        self.cur = self.con.cursor()
        self.cur.execute(f"INSERT INTO log_worksteps(date, type, text) values('{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}', '{event_type}', '{text}')")
        self.con.commit()
        self.cur.close()


    def get_parametr(self, name):
        """
        возвращает значение параметра по его имени
        
        SELECT Value from parametrs where Name = '{name}'
        """
        name = name.replace("'",'"').replace('/n/n','').replace('  ',' ')
        self.cur = self.con.cursor()
        self.cur.execute(f"SELECT Value from parametrs where Name = '{name}'")
        for row in self.cur.fetchall():
            try:
                mess = ast.literal_eval(row[0])
            except:
                mess = row[0]
        self.cur.close()
        return mess


    def get_allparametrs(self):
        """
        возвращает значение всех параметров словарем
        
        SELECT Name, Value from parametrs
        """
        self.cur = self.con.cursor()
        self.cur.execute(f"SELECT Name, Value from parametrs")
        rez = dict()
        for row in self.cur.fetchall():
            try:
                rez[row[0]] = ast.literal_eval(row[1])
            except:
                rez[row[0]] = row[1]
        self.cur.close()
        return rez
