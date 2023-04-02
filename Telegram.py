import telebot
from datetime import datetime
import openai
import time


def startswith(text, word):
    """
    Проверяет начинается ли text с word.
    """
    if len(text) < len(word):
        return False
    return word.lower() == text[:len(word)].lower()


class Exception_Handler:
    def __init__(self, DB):
        self.BD = DB

    def handle(self, e: Exception):
        # Here you can write anything you want for every type of exceptions
        # if isinstance(e, ApiTelegramException):
        #     if e.description == "Forbidden: bot was blocked by the user":
        #         # whatever you want
        self.BD.put_log_worksteps(f'{e}', event_type='Telebot API')

class Telegram:
    def __init__(self, parametrs, BD):
        self.token = parametrs.data['TELEGRAM_TOKEN']
        openai.api_key = parametrs.data['OPENAI_API_KEY']
        self.BD = BD
        # self.bot = telebot.TeleBot(TELEGRAM_TOKEN,exception_handler=log_exceptions)
        self.bot = telebot.TeleBot(self.token,exception_handler=Exception_Handler(self.BD))

        @self.bot.message_handler(commands=["start"])
        def strart(m, res=False):
            self.bot.send_message(m.chat.id, 'Стасик с Вами.\nСам ты олень.')
            print(f'<{m.chat.id}>')
            if str(m.chat.id) == '815870722':
                print('!!!!')
            else:
                print(m.chat.id == '815870722')


        # bot = telebot.TeleBot(TELEGRAM_TOKEN)
        # @bot.message_handler(commands=["statistic"])
        # def channel_statistic(m, res=False):
        #     data = SQL.get_channel_statistic(m.chat.id)
        #     message = f'С {data[1]} по {data[2]}, при общении с ботом, было написано {data[0]} сообщений.'
        #     bot.send_message(m.chat.id, message)
        #     print(f'<{m.chat.id}> {message}')


        # bot = telebot.TeleBot(TELEGRAM_TOKEN)
        # @bot.message_handler(commands=["настройки"])
        # def strart(m, res=False):
        #     print(f'настройки {m.chat.id}')
        #     if str(m.chat.id) == '815870722':
        #         print("/настройки -  вывести список настроек")


        @self.bot.message_handler(content_types=["text"])
        def handle_text(message):
            messenger = 'telegram'
            role = 'user'
            prompt = message.text[4:]
            user_id = str(message.from_user.id)
            user_name = message.from_user.full_name
            channel_id = str(message.chat.id)
            channel_url = message.chat.title if message.chat.type == 'group' else message.chat.type
            insert_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            # Отвечает только пользователям из белого списка или в каналах из белого списка
            if (not(str(message.from_user.id) in parametrs.data['WHITE_USER_ID']) and
                not(str(message.chat.id) in parametrs.data['WHITE_CHANAL_ID'])):
                    self.BD.put_access(insert_date, user_id, user_name, channel_id, messenger, channel_url, False)
                    return False
            self.BD.put_access(insert_date, user_id, user_name, channel_id, messenger, channel_url, True)

            if startswith(message.text, 'Справка'):
                reply = """
        Для общения с ботом, необходимо добавить префикс к своему сообщению:
        Чат - ответит чат бот с языковой моделью gpt-3.5-turbo
        """
                self.bot.send_message(message.chat.id, reply)
                print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} [CHAT] {message.from_user.full_name}: {message.text}")

            if (startswith(message.text, 'Чат') or 
                parametrs.data['CHATBOT_NAME'] in message.text):
                # Записываю сообщение человека в базу        
                role = 'user'
                if startswith(message.text, 'Чат'):
                    prompt = message.text[4:]
                if parametrs.data['CHATBOT_NAME'] in message.text:
                    prompt = message.text.replace(parametrs.data['CHATBOT_NAME'], '')
                user_id = str(message.from_user.id)
                user_name = message.from_user.full_name
                channel_id = str(message.chat.id)
                channel_url = message.chat.title if message.chat.type == 'group' else message.chat.type
                insert_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                print(f'{insert_date} [CHAT] {user_name}: {prompt}')
                self.BD.put_message('user', prompt, messenger, user_id, user_name, channel_id, channel_url, insert_date)
                all_messages = self.BD.get_messages(channel_id)
                # Задаю вопрос боту и получаю ответ
                # completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                # bot.send_chat_action(chat_id=message.chat.id, action='typing', timeout=3) # telegram.ChatAction.TYPING
                try:
                    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=all_messages)
                    # Записываю сообщение бота в базу   
                    user_id = self.bot.user.id
                    user_name = self.bot.user.full_name
                    channel_id = str(message.chat.id)
                    channel_url = message.chat.title if message.chat.type == 'group' else message.chat.type
                    insert_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Частей ответа {len(completion.choices)}")
                    for i in range(len(completion.choices)):
                        role = completion.choices[i].message.role
                        reply = completion.choices[i].message.content
                        self.BD.put_message(role, reply, messenger, user_id, user_name, channel_id, channel_url, insert_date)
                        
                        self.bot.send_message(message.chat.id, reply)
                        print(f'{insert_date} [CHAT] {user_name}: {reply}')
                except Exception as e:
                    print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] {e}")
                    self.BD.put_log_worksteps(f'{e}', event_type='OpenAI Error')
                    role = 'Error'
                    reply = str(e).replace("'",' ').replace('"',' ')
                    time.sleep(2)
                    user_id = self.bot.user.id
                    user_name = self.bot.user.full_name
                    channel_id = str(message.chat.id)
                    channel_url = message.chat.title if message.chat.type == 'group' else message.chat.type
                    insert_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    self.BD.put_message(role, reply, messenger, user_id, user_name, channel_id, channel_url, insert_date)

                    self.bot.send_message(message.chat.id, reply)
                    print(f'{insert_date} [CHAT] {user_name}: {reply}')

            if startswith(message.text, 'Статистика'):
                data = self.BD.get_channel_statistic(channel_id)
                message = f'С {data[1]} по {data[2]}, при общении с ботом, было написано {data[0]} сообщений.'
                data = self.BD.get_channel_statistic(channel_id, role='user')
                message = f'{message}\nЗапросов: {data[0]}'
                data = self.BD.get_channel_statistic(channel_id, role='assistant')
                message = f'{message}\nОтветов: {data[0]}'
                self.bot.send_message(channel_id, message)
                print(f'<{channel_id}> {message}')
        
        # @self.bot.exception_handler()

    def run(self):
        self.bot.polling()
