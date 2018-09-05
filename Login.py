from flask import Flask, request, session, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
import pymysql
from db_helper import DB_Helper
from NumberToWord import *


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'abc'



conn = pymysql.connect(host='163.239.169.54', port=3306, user='s20131533', passwd='s20131533',db='number_to_word', charset='utf8')
db_helper = DB_Helper(conn)

cur = conn.cursor()




@app.route('/main')
def main():
    if 'username' in session.keys() and 'password' in session.keys():
        return session['username'] + '님 로그인을 환영합니다.'
    else:
        return '로그인 하십시오.'


@app.route('/logging')
def logging_test():
    test = 1
    app.logger.debug('디버깅 필요')
    app.logger.warning(str(test) + " 라인")
    app.logger.error('에러발생')
    return "로깅 끝"

@app.route('/login')
def login_form():
    return render_template('login_form.html')


@app.route('/check', methods = ['POST','GET'])
def login():
    if request.method == 'POST':

        users = {}

        cur.execute("select * from user_info")
        for data in cur:
            users[data[0]]= data[1]


        if request.form['username'] in users.keys() and request.form['password'] == users[request.form['username']]:
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']

            return render_template('main_page.html', username=session['username'])
        else:
            error_msg = '로그인 정보가 맞지 않습니다.'
            return render_template('login_form.html', error_msg=error_msg)
    else:
        return '잘못된 접근'


@app.route('/change', methods = ['POST', 'GET'])
def change():
    if request.method == 'POST':
        session['input'] = request.form['input']
        input_str = session['input']

        output_list = NumberToWord(input_str)
        output_str = "\n".join(output_list)

        return render_template('main_page.html', username=session['username'], input=input_str, output=output_str)
    else:
        return '잘못된 접근'


@app.route('/text_board')
def text_board():

    data_article = ()

    board_total = []
    board_each_line = []

    text_num = 1

    cur.execute("select * from ArticleTable")
    data_article = cur.fetchall()
    for row_article in data_article:
        article_id = row_article[0]
        article_url = row_article[1]
        article_title = row_article[2]
        article_uploaded_date = row_article[3]
        article_collected_date = row_article[4]


        cur.execute("select * from SentenceTable where ArticleTable_article_id=" + str(article_id))
        data_sent = cur.fetchall()
        for row_sent in data_sent:

            board_each_line = []

            sent_id = row_sent[0]
            sent_original = row_sent[1]

            #sent_converted = row_sent[2]

            sent_converted_list = NumberToWord(sent_original)
            sent_converted = "\n".join(sent_converted_list)


            sent_modified_date = row_sent[3]
            sent_check = row_sent[4]
            sent_ambiguity = row_sent[5]
            sent_views = row_sent[6]


            board_each_line.append(text_num)                    # row[0]
            board_each_line.append(sent_original)               # row[1]
            board_each_line.append(sent_converted)              # row[2]
            board_each_line.append(article_id)                  # row[3]
            board_each_line.append(article_collected_date)      # row[4]
            board_each_line.append(sent_modified_date)          # row[5]
            board_each_line.append(sent_views)                  # row[6]


            board_total.append(board_each_line)

            text_num += 1


    print(board_total)

    return render_template('text_board.html', board_total=board_total)


@app.route('/text_convert')
def text_convert():
    return render_template('text_convert.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('main'))





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)