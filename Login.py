from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
import pymysql
from db_helper import DB_Helper
from NumberToWord import *


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'abc'



conn = pymysql.connect(host='163.239.169.54', port=3306, user='s20131533', passwd='s20131533',db='number_to_word', charset='utf8')
db_helper = DB_Helper(conn)

#cur = conn.cursor()


def reload_board_total():

    board_total = []

    rows_article = db_helper.get_every_rows_from_table('ArticleTable')
    for row_article in rows_article:
        article_id = row_article[0]
        article_url = row_article[1]
        article_title = row_article[2]
        article_uploaded_date = row_article[3]
        article_collected_date = row_article[4]

        # Article의 id와 연결되어있는 Sentence
        rows_sent = db_helper.get_every_rows_from_sentence_by_id(article_id)
        for row_sent in rows_sent:
            board_each_line = {}

            board_each_line['sent_id'] = row_sent[0]
            board_each_line['sent_original'] = row_sent[1]
            board_each_line['sent_converted'] = row_sent[2]

            board_each_line['sent_modified_date'] = row_sent[3]
            if board_each_line['sent_modified_date'] == '0000-00-00 00:00:00':
                board_each_line['sent_modified_date'] = '-'

            board_each_line['sent_confirm'] = row_sent[4]
            board_each_line['sent_ambiguity'] = row_sent[5]
            board_each_line['sent_converted_count'] = row_sent[6]
            board_each_line['sent_is_added'] = row_sent[7]

            board_each_line['article_id'] = article_id

            board_each_line['article_collected_date'] = article_collected_date
            if board_each_line['article_collected_date'] == '0000-00-00 00:00:00':
                board_each_line['article_collected_date'] = '-'

            board_total.append(board_each_line)



    return board_total



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
def login():
    return render_template('login_form.html')



@app.route('/login_check', methods = ['POST','GET'])
def login_check():
    if request.method == 'POST':

        users = {}

        rows = db_helper.get_every_rows_from_table('user_info')
        for row in rows:
            users[row[0]]= row[1]


        # 유저이름과 그에 해당하는 패스워드가 일치하는지 확인
        if request.form['username'] in users.keys() and request.form['password'] == users[request.form['username']]:
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            #return render_template('main_page.html', username=session['username'])
            return redirect(url_for('text_board'))
        else:
            error_msg = '로그인 정보가 맞지 않습니다.'
            return render_template('login_form.html', error_msg=error_msg)

    elif request.method == 'GET':
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


@app.route('/text_board', methods = ['POST', 'GET'])
def text_board():
    print(request.method)
    username = session['username']

    if request.method == 'GET':

        board_total = reload_board_total()

        return render_template('text_board.html', board_total = board_total, username = username)



    elif request.method == 'POST':
        if request.form['ORIGINAL'] == '' or request.form['CONVERTED'] == '':
            flash('텍스트를 입력해 주세요.','warning')
            return redirect(url_for('text_edit',id=session['sent_id']))

        id = session['sent_id']

        sent_converted_count = db_helper.get_data_from_sentence_by_id('sent_converted_count', id)
        sent_converted_count = sent_converted_count + 1
        db_helper.update_sent_converted_count(sent_converted_count, id)


        if 'ambiguity' in request.form:
            db_helper.update_sent_ambiguity(id)


        original_text = request.form['ORIGINAL']
        converted_text = request.form['CONVERTED']

        db_helper.update_sent_converted(converted_text, id)
        db_helper.update_sent_modified_date(id)
        db_helper.update_sent_confirm(id)


        board_total = reload_board_total()


        return render_template('text_board.html', board_total = board_total)



@app.route('/text_board/<id>/edit')
def text_edit(id):


    session['sent_id'] = id

    sent_ambiguity = db_helper.get_data_from_sentence_by_id('sent_ambiguity', id)

    original_text = db_helper.get_data_from_sentence_by_id('sent_original', id)

    converted_list = NumberToWord(original_text)
    converted_text = "\n".join(converted_list)


    return render_template('text_convert.html', original_text = original_text, converted_text = converted_text)


@app.route('/text_board/<id>/delete')
def text_delete(id):

    db_helper.delete_sent_by_id(id)


    return redirect(url_for('text_board'))
    #return render_template('text_board.html', board_total = board_total)


@app.route('/text_board/create', methods = ['GET', 'POST'])
def text_create():
    print(request.method)

    if request.method == 'GET':
        return render_template('text_create.html')

    elif request.method == 'POST':
        if request.form['text_register'] == '':
            flash('텍스트를 입력해주세요.', 'warning')
            return render_template('text_create.html')
            #return redirect(url_for('text_create'))

        added_dict = {}

        text_register = request.form['text_register']
        print(text_register)


        largest_sent_id = db_helper.get_largest_sent_id()


        added_dict['sent_id'] = largest_sent_id + 1
        added_dict['sent_original'] = text_register

        # 기사로부터 가져온 것이 아니라 새로 추가한 것이기 때문에 1 로 설정, article_id는 0으로 설정
        added_dict['sent_is_added'] = 1
        added_dict['ArticleTable_article_id'] = 0


        db_helper.insert_new_text(added_dict)


        return redirect(url_for('text_board'))




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