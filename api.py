# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals
import random
import datetime
# Импортируем модули для работы с JSON и логами.
import json
import logging
x=''
date=''
time=''
#задаем списки фраз
say_yes = [ 'да','хорошо','давайте','ок','согласен','я согласен',\
           'давайте','ага','согласна','угу','я согласна','валяй','валяйте','поехали','пиши']
say_why = ['это обязательно?', 'это обязательно','зачем','зачем?',\
           'а зачем?','зачем это нужно','а зачем?','а зачем это нужно?',\
           'зачем это нужно?','к чему это?','что это?']
say_no = ['нет','низачто','никогда','я против','не хочу','не буду','против']
say_recommend = ['назначение','назначаю','препарат','рекомендации','препараты',
        'рекомендую','рекомендация', 'лечение']
say=['Я записала "%s". Что-то ещё? ', 'Вы сказали "%s". Что-то ещё? ',\
     'Я записала "%s". Раскажете что-то ещё? ',]
t=1
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])

def main():
    global t
# Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    if request.json['session']['new'] or t ==1:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        handle_dialog1(request.json, response)
    else:
        handle_dialog2(request.json, response)
        

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog1(req, res):
    user_id = req['session']['user_id']
    global x
    global date
    global time
    global t

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Да",
                "Зачем это нужно?",
                "Причина обращения",
                "Недомогание началось...",
                "Сейчас я чувувствую себя...",
                "Это всё",
                "Запись завершена",     
            ]
        }

        d=datetime.datetime.today()
        # Локальное время Алисы "timezone": "UTC", х.з. как переопределить, поэтому костыль +4
        n=datetime.datetime.now() + datetime.timedelta(hours = 4)
        date = str(d.day)+'-'+str(d.month)+'-'+str(d.year)
        time = str(n.hour)+':'+str(n.minute)
        x=date[:]+'\nВремя приёма: '+time+'\n'
        res['response']['text'] = 'Добрый вечер! Я голосовой помошник врача. Скажите, пожалуйста, согласны ли вы на запись приема?'
        x+='Пациент: '+str(user_id)[-5:]+'\n'
        res['response']['buttons'] = get_suggests(user_id) 
        t=1
        return

    ## Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in say_why:
        
        res['response']['text'] ='Это не обязательно, но у врача будет больше времени на постановку диагноза. Попробуем?' 
        res['response']['buttons'] = get_suggests(user_id)
        t = 1
        return 
    
    if req['request']['original_utterance'].lower() in say_no:
        res['response']['text'] ='Ничего страшного. Будем работать по старинке. Хотя это помогло бы врачу... ' 
        t = 1
        return 
    if req['request']['original_utterance'].lower() in say_yes:
        res['response']['text'] ='Спасибо. Давайте начнем. Укажите причину обращения?'
        x += '\nПричина обращения - '
        t = 2
        return
    # Если нет, записываем информацию!
    res['response']['text'] = 'Извините, я не расслышала'
    res['response']['buttons'] = get_suggests(user_id)

def handle_dialog2(req2, res2):
    user_id = req2['session']['user_id']
    global x
    global date
    global time    

    if req2['request']['original_utterance'].lower() in [
        'диагноз',
        'предварительный диагноз',

    ]:
        res2['response']['text'] ='Слушаю:'
        x+='\nДиагноз - '
        return  

    if req2['request']['original_utterance'].lower() in say_recommend:
        res2['response']['text'] ='Слушаю:'
        x+='\nНазначение - '
        return
    if req2['request']['original_utterance'].lower() in [
        'прием завершен',
        'прием завершен',
        'запись завершена',
        'досвидания',
    ]:
        res2['response']['text'] ='Отлично! Вот что я записала:'+x
        #завершаем сессию
        response = {
            "version": request.json['version'],
            "session": request.json['session'],
            "response": {
            "end_session": True
            }
        }
        #записываем информацию в файл
        diagn_start = x.find('Диагноз -')
        if diagn_start != -1:
            diagn_end = x.find(';',diagn_start)
            diagn=x[diagn_start+9:diagn_end]
            x = x[:diagn_start] +x[diagn_end:]
        else:
            diagn = '-'        
        filename = date + str(user_id)[4:] + '.json'
        with open(filename,'w') as f:
            json.dump({'date':date,'time':time,'else':x,'user_id':user_id,'diagnoz':diagn}, f)

        return
    # Обрабатываем ответ пользователя.
    if req2['request']['original_utterance'].lower() in [
        'все',
        'это все',
        'вроде все',
        'закончил',

    ]:
        res2['response']['text'] ='Спасибо, я всё записала '
        return
    # Если нет, записываем информацию!
    res2['response']['text'] = 'Я записала "%s". Что-то ещё?' % (
        req2['request']['original_utterance']
    )
    if req2['request']['original_utterance']!='ping':
        x +=req2['request']['original_utterance']+'; '
    res2['response']['buttons'] = get_suggests(user_id)

# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Скайнет",
            "url": "https://market.yandex.ru/search?text=скайнет",
            "hide": True
        })

    return suggests
