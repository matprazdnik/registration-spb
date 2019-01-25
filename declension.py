#!/usr/bin/env python3

import db
import config

conn, cur = db.mysql_init()
while True:
    cur.execute("select id, school from users where id>22 and school2='' limit 1")
    u = {}
    for r in cur.fetchall():
        u['id'], u['school'] = r[0], r[1]
    if not 'id' in u:
        break
    try:
        sn = int(u['school'])
    except:
        sn = False
    res = ''
    if sn != False:
        res = 'школы ' + u['school']
    elif u['school'] in ['ГФМЛ 30', 'ПФМЛ 239', 'ФМЛ 366', 'ЛНМО', 'ЦИВ', 'ЧОУ Шостаковичей', 'ФМЛ']:
        res = u['school']
    elif u['school'].split()[0] == 'гимназия':
        res = 'гимназии ' + u['school'].split()[1]
    elif u['school'].split()[0] == 'лицей':
        res = 'лицея ' + u['school'].split()[1]
    elif u['school'] in ['Экономики и права', 'ИзНаКурНож']:
        res = 'школы ' + u['school']
    elif u['school'] in ['Альма Матер']:
        res = 'гимназии ' + u['school']
    elif u['school'] in ['Вторая гимназия']:
        res = 'Второй гимназии'
    else:
        print('! ' + str(u['id']) + ': ' + u['school'])
        break
    print('+ ' + str(u['id']) + ': ' + u['school'] + ' -> ' + res)
    cur.execute('update users set school2=%s where id=%s', [res, u['id']])
    conn.commit()

db.mysql_close(conn, cur)
