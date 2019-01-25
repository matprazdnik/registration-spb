#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cymysql
from flask import Flask, url_for, render_template, request
import cgi
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from subprocess import call

import config
import db

letters = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮёЁ-.1234567890 '
def texify(a):
    s = ''
    for c in a:
        if c in letters:
            s += c
    return s

conn, cur = db.mysql_init()
cur.execute('select id, first_name, last_name, gender, school, grade, grade2, state from users where state=0 limit 1')
for e in cur.fetchall():
    user_id = e[0]
    first_name = e[1]
    last_name = e[2]
    gender = e[3]
    school = e[4]
    grade = e[5]
    grade2 = e[6]
    state = e[7]

    user_hash = user_id * 1000000007 % 301703

    cur.execute('update users set state = 10 where id=%s', [str(user_id)])
    conn.commit()
    file_name = 'title' + str(user_hash) + ''
    tex = open(file_name + '.tex', mode='w', encoding='utf-8')
    tex.write('\\documentclass[a4paper,12pt]{article}\n\n')
    tex.write('\\usepackage[utf8]{inputenc}\n')
    tex.write('\\usepackage[T2A]{fontenc}\n')
    tex.write('\\usepackage[top=0.69in,bottom=0.69in,left=1in,right=1in]{geometry}\n')
    tex.write('\\usepackage{graphicx}\n\n')
    tex.write('\\pagestyle{empty}\n\n')
    tex.write('\\begin{document}\n')
    tex.write('\\begin{center}\n')
    tex.write('\\begin{tabular}{ccc}\n')
    tex.write('{\\Huge [' + texify(last_name)[:1] + ']} & {\\huge МАТЕМАТИЧЕСКИЙ ПРАЗДНИК} & {\\Huge [' + str(grade) + ']} \\\\\n')
    tex.write('\\end{tabular}\n\n')
    tex.write('\\vskip 1cm\n')
    tex.write('{\large Санкт-Петербург, 21 февраля 2016 года}\n\n')
    tex.write('\\vskip 1cm\n')
    tex.write('титульный лист участника\n\n')
    tex.write('\\vskip 1cm\n')
    tex.write('{\huge \\bf ' + texify(first_name) + ' ' + texify(last_name) + '}\n\n')
    tex.write('{\large (' + texify(school) + ', ' + texify(grade2) + ' класс)}\n\n')
    tex.write('\\vskip 2cm\n')
    tex.write('{\\Large Код бланка} \n')
    b = '\\begin{tabular}{|c|}\n' + ' \\hline\n' + ' {\\Huge \\phantom{X} } \\\\\n' + ' \\hline\n' + '\\end{tabular}\n'
    tex.write(b + b + b + b + ' --- ' + b + b + '\n\n')
    tex.write('(просим переписать с титульного листа работы)\n\n')
    tex.write('\\vskip 7cm\n\n')
    tex.write('Просим распечатать этот титульный лист и принести его с собой на\n')
    tex.write('Математический праздник в \\\\\n')
    tex.write(str(grade) + ' классе в Физико-математическом лицее 30.\n\n')
    tex.write('\\vskip 1cm\n')
    tex.write('{\\it Начало Праздника в 10 часов утра. На решение задач дается 2 часа.\n')
    tex.write('Завершается программа Праздника около 18 часов.\n\n')
    tex.write('Результаты после закрытия~--- на сайте} \\texttt{spbtc.ru/matrpazdnik}\n\n')
    tex.write('\\vskip 1cm\n')
    tex.write('(регистрация ' + str(user_hash) + ')\\\\\n')
    tex.write('\\end{center}\n')
    tex.write('\\end{document}\n')
    tex.close()
  
    call(['pdflatex', file_name + '.tex'])
    call(['pdf2ps', file_name + '.pdf'])
  
    call(['mv', '-f', file_name + '.pdf', 'static/'])
    call(['mv', '-f', file_name + '.ps', 'static/'])
    call(['rm', '-f', file_name + '.aux', file_name + '.log', file_name + '.tex'])

db.mysql_close(conn, cur)
