from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
import pymysql
import os
from db_helper import DB_Helper
from flask_paginate import Pagination, get_page_parameter, get_page_args
from NumberToWord import *


app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(24)



conn = pymysql.connect(host='163.239.169.54',
                       port=3306,
                       user='s20131533',
                       passwd='s20131533',
                       db='number_to_word',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)

db_helper = DB_Helper(conn)

cur = conn.cursor()


def reload_board_total():

    username = session['username']

    sql = "SELECT count(*) as total_count FROM SentenceTable"
    cur.execute(sql)
    total_count = cur.fetchone()['total_count']

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    board_total = db_helper.call_board(page, per_page)

    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=total_count,
                            record_name='Sentences',
                            bs_version=4,
                            alignment='center',
                            show_single_page=True)

    return render_template('text_board.html', board_total=board_total, username=username, pagination=pagination, page=page)



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


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    session.pop('password', None)
    flash('로그아웃 되었습니다.', 'alert-success')
    return redirect(url_for('login'))



@app.route('/login_check', methods = ['POST','GET'])
def login_check():
    if request.method == 'POST':

        users = {}

        rows = db_helper.select_every_rows_from_table('user_info')
        for row in rows:
            users[row['username']]= row['password']


        # 유저이름과 그에 해당하는 패스워드가 일치하는지 확인
        if request.form['username'] in users.keys() and request.form['password'] == users[request.form['username']]:
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return redirect(url_for('text_board', page = 1))
        else:
            error_msg = '로그인 정보가 맞지 않습니다.'
            flash(error_msg, 'alert-danger')
            return render_template('login_form.html')

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
    print(request.method + '\t' + request.url)


    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        return redirect(url_for('login'))

    username = session['username']


    if request.method == 'GET':
        return reload_board_total()



    elif request.method == 'POST':
        if request.form['ORIGINAL'] == '' or request.form['CONVERTED'] == '':
            flash('텍스트를 입력해 주세요.','alert-danger')

            id = session['sent_id']
            original_text = db_helper.select_data_from_table_by_id('sent_original', 'SentenceTable', id)

            converted_list = NumberToWord(original_text)
            converted_text = "\n".join(converted_list)

            return render_template('text_edit.html', original_text=original_text, converted_text=converted_text, page=page)


        id = session['sent_id']

        sent_converted_count = db_helper.select_data_from_table_by_id('sent_converted_count','SentenceTable', id)
        sent_converted_count = sent_converted_count + 1
        db_helper.update_sent_converted_count(sent_converted_count, id)


        if 'ambiguity' in request.form:
            db_helper.update_sent_ambiguity(1, id)
        else:
            db_helper.update_sent_ambiguity(0, id)



        original_text = request.form['ORIGINAL']
        converted_text = request.form['CONVERTED']

        db_helper.update_sent_converted(converted_text, id)
        db_helper.update_sent_modified_date(id)
        db_helper.update_sent_confirm(id)


        return reload_board_total()




@app.route('/text_board/<id>/edit', methods=['GET'])
def text_edit(id):

    session['sent_id'] = id

    print('page' + str(request.args.get('page')))
    page = request.args.get('page')


    original_text = db_helper.select_data_from_table_by_id('sent_original', 'SentenceTable', id)

    converted_list = NumberToWord(original_text)
    converted_text = "\n".join(converted_list)


    return render_template('text_edit.html', original_text = original_text, converted_text = converted_text, page = page)


@app.route('/text_board/<id>/delete', methods=['GET'])
def text_delete(id):

    db_helper.delete_sent_by_id(id)

    page = request.args.get('page')
    print('deleted page : ' + str(page))


    return redirect(url_for('text_board', page = page))


@app.route('/text_board/create', methods = ['GET', 'POST'])
def text_create():
    print(request.method)
    page = request.args.get('page')


    if request.method == 'GET':
        return render_template('text_create.html', page = page)



    elif request.method == 'POST':
        if request.form['text_create'] == '':
            flash('텍스트를 입력해주세요.', 'alert-danger')
            return render_template('text_create.html', page = page)
            #return redirect(url_for('text_create'))

        added_dict = {}

        text_create = request.form['text_create']
        print(text_create)


        largest_sent_id = db_helper.select_largest_sent_id()


        added_dict['sent_id'] = largest_sent_id + 1
        added_dict['sent_original'] = text_create

        # 기사로부터 가져온 것이 아니라 새로 추가한 것이기 때문에 1 로 설정, article_id는 0으로 설정
        added_dict['sent_is_added'] = 1
        added_dict['ArticleTable_article_id'] = 0


        db_helper.insert_new_text(added_dict)


        return redirect(url_for('text_board', page = page))


@app.route('/text_board/search', methods=['GET'])
def text_search():


    search_msg = request.args.get('query')
    page = request.args.get('page')


    # 빈 문자열 입력시 모든 Sentence 출력
    if search_msg.strip() == "":
        return redirect(url_for('text_board', page = page))

    username = session['username']


    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10



    board_search = db_helper.call_board_search(page, per_page, search_msg)

    total_count = len(board_search)
    print(total_count)


    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=total_count,
                            record_name='Sentences',
                            bs_version=4,
                            alignment='center',
                            show_single_page=True)



    return render_template('text_board.html', board_total = board_search, username = username, pagination = pagination, page = page)











if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)