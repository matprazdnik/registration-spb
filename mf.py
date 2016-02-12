from flask import Flask, url_for, render_template, request, make_response, redirect
import cgi
import hashlib
import time
import random
import string
import urllib
import json

import lang
import config
import db

mf = Flask(__name__)

@mf.route('/')
def index():
    content = ''
    content += lang.lang['index_intro']
    content += '<div><b><a href="' + config.base_url + '/reg">' + lang.lang['index_registration'] + '</a></b></div>\n'
    return render_template('template.html', title=lang.lang['index_title'], content=content)

def get_html_form(data):
    res = ''
    res += '<form action="' + config.base_url + '/reg" method="POST">\n'
    res += '<table>\n'
    res += '  <tr><td>Фамилия</td>    <td><input type="text" name="last_name" value="' + cgi.escape(data['last_name']) + '"></td></tr>\n'
    res += '  <tr><td>Имя</td>        <td><input type="text" name="first_name" value="' + cgi.escape(data['first_name']) + '"></td></tr>\n'
    res += '  <tr><td>Отчество</td>   <td><input type="text" name="patronymic" value="' + cgi.escape(data['patronymic']) + '"></td></tr>\n'
    res += '  <tr><td>Пол</td>        <td><select name="gender"><option value="ж">женский</option><option value="м">мужской</option></></td></tr>\n'
    res += '  <tr><td>Класс</td>      <td><select name="grade"><option value="6">6 и младше</option><option value="7">7</option></></td></tr>\n'
    res += '  <tr><td>Город</td>      <td><input type="text" name="city" value="' + cgi.escape(data['city']) + '"></td></tr>\n'
    res += '  <tr><td>Школа</td>      <td><input type="text" name="school" value="' + cgi.escape(data['school']) + '"></td></tr>\n'
    res += '  <tr><td>Класс</td>      <td><input type="text" name="grade2" value="' + cgi.escape(data['grade2']) + '"></td></tr>\n'
    res += '  <tr><td>E-mail</td>     <td><input type="text" name="email" value="' + cgi.escape(data['email']) + '"></td></tr>\n'
    res += '  <tr><td>Комментарии</td><td><textarea name="comment" cols="30" rows="5" placeholder="В каких кружках вы занимаетесь? Что бы вы хотели добавить?">' \
        + cgi.escape(data['comment']) + '</textarea></td></tr>\n'
    res += '  <tr><td></td><td><input type="checkbox" name="agree_shoes">Я знаю, что необходимо взять с собой сменную обувь</td></tr>\n'
    res += '  <tr><td></td><td><input type="submit" value="Зарегистрироваться"></td></tr>\n'
    res += '</table>\n'
    res += '</form>\n'
    return res

def check_form(data):
    for f in ['last_name', 'first_name', 'patronymic', 'school', 'grade2', 'email']:
        if data[f] == '':
            return False, lang.lang['error_required_personal'] + f
    if not data['grade'] in ['6', '7']:
        return False, lang.lang['error_incorrect_grade']
    if not data['gender'] in ['м', 'ж']:
        return False, lang.lang['error_incorrect_grade']
    if data['agree_shoes'] == '':
        return False, lang.lang['error_shoes_required']
    return True, ''

def do_reg(data):
    conn, cur = db.mysql_init()
    fields = ['last_name', 'first_name', 'patronymic', 'gender', 'grade', 'city', 'school', 'grade2', 'email', 'comment', 'state', 'reg_date']
    data['state'] = 0
    data['reg_date'] = time.time()
    cur.execute('insert into users(' + ', '.join(fields) + ') values (' + ', '.join(['%s'] * len(fields)) + ')', [data[f] for f in fields])
    cur.execute ('select last_insert_id()')
    user_id = cur.fetchall()[0][0]
    conn.commit()
    db.mysql_close(conn, cur)
    return user_id

def get_user_hash(user_id):
    return user_id * 1000000007 % 301703

@mf.route('/reg', methods=['GET', 'POST'])
def reg():
    data = {}
    fields = ['last_name', 'first_name', 'patronymic', 'gender', 'grade', 'school', 'grade2', 'email', 'comment', 'agree_shoes', 'city']
    for f in fields:
        try:
            data[f] = request.form[f]
        except:
            data[f] = ''
    if data['city'] == '':
        data['city'] = 'Санкт-Петербург'

    content = ''
    if request.method == 'POST':
        ok, error = check_form(data)
        if ok:
            user_id = do_reg(data)
            content += '<div>' + lang.lang['reg_done'] + '</div>\n'
            user_hash = get_user_hash(user_id)
            link = config.base_url + '/static/title' + str(user_hash) + '.pdf'
            content += '<div>Ваш титульный лист будет доступен по ссылке: <a href="' + link + '">' \
                + link + '</a>. Пожалуйста, распечатайте его и принесите с собой на Матпраздник.</div>\n'
        else:
            content += '<div><span class="error">' + error + '</span></div>'
            content += get_html_form(data)
    else:
        content += get_html_form(data)
    return render_template('template.html', title=lang.lang['index_title'], content=content)

def create_auth_token(user_id):
    day = int(time.time() / (24 * 60 * 60))
    return hashlib.md5((str(user_id) + ':' + str(day) + ':' + config.auth_salt).encode()).hexdigest()

def check_auth():
    try:
        user_id = request.cookies.get('mf_user_id')
        auth_token = request.cookies.get('mf_auth_token')
    except:
        return None
    if auth_token != create_auth_token(user_id):
        return None
    return user_id

@mf.route('/auth/vk_start')
def vk_start():
    return redirect( \
        'https://oauth.vk.com/authorize?client_id=' + \
        config.vk_app_id + '&display=page&response_type=code&redirect_uri=' + \
        config.base_url + '/auth/vk_done')

@mf.route('/auth/vk_done')
def vk_done():
    try:
        code = request.args.get('code', '')
    except:
        code = 'None'
    vk_oauth_url = \
        'https://oauth.vk.com/access_token?client_id=' + \
        config.vk_app_id + '&client_secret=' + config.vk_client_secret + \
        '&redirect_uri=' + config.base_url + '/auth/vk_done&code=' + \
        code
    res = json.loads(urllib.request.urlopen(vk_oauth_url).read().decode())
    if 'error' in res:
        error_content = 'Failed auth: ' + str(res['error_description'])
        return render_template('template.html', title='Failed auth', content=error_content)
    user_id = 'vk:' + str(res['user_id'])
    auth_token = create_auth_token(user_id)
    resp = make_response(redirect(config.base_url))
    resp.set_cookie('mf_auth_token', auth_token)
    resp.set_cookie('mf_user_id', user_id)
    return resp

@mf.route('/admin')
def admin():
    user_id = check_auth()
    if not user_id in config.admin_ids:
        content = '<div>Ты недостаточно прав.</div><div><a href="' + config.base_url + '/auth/vk_start">Войти</a></div></div>\n'
        return render_template('template.html', title='Недостаточно прав', content=content)
    conn, cur = db.mysql_init()
    fields = ['id', 'first_name', 'last_name', 'grade', 'school', 'email', 'reg_date']
    cur.execute('select ' + ', '.join(fields) + ' from users where id > 22 order by grade, id')
    content = ''
    users = []
    for u in cur.fetchall():
        i = 0
        user = {}
        for f in fields:
            user[f] = u[i]
            i += 1
        user['reg_date'] = time.strftime('%b %d %H:%M:%S', time.localtime(int(user['reg_date'])))
        users.append(user)
    names = {6: {}, 7: {}}
    for u in users:
        name = u['first_name'] + ' ' + u['last_name']
        grade = int(u['grade'])
        if not name in names[grade]:
            names[grade][name] = True
    content += '<table>\n' + '<tr>' + ''.join(['<th>' + f + '</th>' for f in fields]) + '</th>'
    content += '\n'.join(['<tr>' + ''.join(['<td>' + cgi.escape(str(u[f])) + '</td>' for f in fields]) + '</tr>\n' for u in users])
    content += '</table>\n'
    for g in [6, 7]:
        content += '<div>' + str(len(names[g])) + ' различных имен-фамилий в ' + str(g) + ' классе</div>'
    content += '<div>' + str(len(names[6]) + len(names[7])) + ' различных имен-фамилий всего</div>'
    db.mysql_close(conn, cur)
    return render_template('template.html', title=lang.lang['admin_title'], content=content)

if __name__ == '__main__':
    webc = config.config['web']
    mf.debug = webc['debug']
    mf.run(host=webc['host'], port=webc['port'])
