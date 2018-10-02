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

sid1_count = {'정치' : 0, '경제' : 0, '사회' : 0, '생활/문화' : 0, '세계' : 0, 'IT/과학' : 0}

sid2_count = {'청와대' : 0, '국회/정당' : 0, '북한' : 0, '행정' : 0, '국방/외교' : 0, '정치 일반' : 0,
              '금융' : 0, '증권' : 0, '산업/재계' : 0, '중기/벤처' : 0, '부동산' : 0, '글로벌 경제' : 0, '생활 경제' : 0, '경제 일반' : 0,
              '사건사고' : 0, '교육' : 0, '노동' : 0, '언론' : 0, '환경' : 0, '인권/복지' : 0, '식품/의료' : 0, '지역' : 0, '인물' : 0, '사회 일반' : 0,
              '건강정보' : 0, '자동차/시승기' : 0, '도로/교통' : 0, '여행/레저' : 0, '음식/맛집' : 0, '패션/뷰티' : 0, '공연/전시' : 0, '책' : 0, '종교' : 0, '날씨' : 0, '생활문화 일반' : 0,
              '아시아/호주' : 0, '미국/중남미' : 0, '유럽' : 0, '중동/아프리카' : 0, '세계 일반' : 0,
              '모바일' : 0, '인터넷/SNS' : 0, '통신/뉴미디어' : 0, 'IT 일반' : 0, '보안/해킹' : 0, '컴퓨터' : 0, '게임/리뷰' : 0, '과학 일반' : 0}



def reload_text_board(search_msg):

    username = session['username']
    article_id = request.args.get('article_id')

    # 딕셔너리 초기화
    for i in sid1_count:
        sid1_count[i] = 0
    for i in sid2_count:
        sid2_count[i] = 0



    # article_sid1 각각의 개수 저장
    article_sid1_column = db_helper.select_one_column('article_sid1', 'ArticleTable')
    for row in article_sid1_column:
        key = row['article_sid1']

        if key != '':
            sid1_count[key] += 1


    # article_sid2 각각의 개수 저장
    article_sid2_column = db_helper.select_one_column('article_sid2', 'ArticleTable')
    for row in article_sid2_column:
        key = row['article_sid2']

        if key != '':
            sid2_count[key] += 1




    # 공통 코드 ==========================================
    page = request.args.get('page', type=int, default=1)
    article_board_page = request.args.get('article_board_page')
    per_page = 10

    asc1_desc0 = request.args.get('asc1_desc0')
    col_name = request.args.get('col_name')
    # ===================================================

    # 검색한 게시글 반환
    if search_msg is not None:
        print('검색')
        search_msg_escaped = conn.escape_string(search_msg)

        sql = "SELECT count(*) as total_count FROM SentenceTable " \
              "WHERE (sent_original LIKE '%%%s%%' AND sent_confirm = 0) OR (sent_original LIKE '%%%s%%' AND sent_confirm = 1)" % (search_msg_escaped, search_msg_escaped)
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']


        board_search = db_helper.call_search_sentence(page, per_page, search_msg, asc1_desc0, col_name)


        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Sentences',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)


        return render_template('text_board.html',
                               board_total=board_search,
                               username=username,
                               pagination=pagination,
                               page=page,
                               search_msg=search_msg,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count,
                               article_id=article_id,
                               article_board_page=article_board_page)


    # 특정 기사를 클릭한 경우
    elif article_id is not None:
        print('특정 기사 클릭')
        sql = "SELECT COUNT(*) as total_count FROM SentenceTable WHERE ArticleTable_article_id = %s" % article_id
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']

        article_title = db_helper.select_data_from_table_by_id('article_title', 'ArticleTable', article_id)

        board_article = db_helper.call_sentence_by_article_id(page, per_page, article_id, asc1_desc0, col_name)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Sentences',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)

        return render_template('text_board.html',
                               board_total=board_article,
                               username=username,
                               pagination=pagination,
                               page=page,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count,
                               article_title=article_title,
                               article_id=article_id,
                               article_board_page=article_board_page)



    # 게시글 전체 반환
    else:
        print('전체')
        sql = "SELECT count(*) as total_count FROM SentenceTable"
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']

        board_total = db_helper.call_every_sentence(page, per_page, asc1_desc0, col_name)


        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Sentences',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)


        return render_template('text_board.html',
                               board_total=board_total,
                               username=username,
                               pagination=pagination,
                               page=page,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count,
                               article_id=article_id,
                               article_board_page=article_board_page)




def reload_article_board(search_msg):

    username = session['username']

    sid1 = request.args.get('sid1')
    sid2 = request.args.get('sid2')


    # 딕셔너리 초기화
    for i in sid1_count:
        sid1_count[i] = 0
    for i in sid2_count:
        sid2_count[i] = 0


    # article_sid1 각각의 개수 저장
    article_sid1_column = db_helper.select_one_column('article_sid1', 'ArticleTable')
    for row in article_sid1_column:
        key = row['article_sid1']

        if key != '':
            sid1_count[key] += 1

    # article_sid2 각각의 개수 저장
    article_sid2_column = db_helper.select_one_column('article_sid2', 'ArticleTable')
    for row in article_sid2_column:
        key = row['article_sid2']

        if key != '':
            sid2_count[key] += 1




    # 공통 코드 =========================================
    page = request.args.get('page', type=int, default=1)
    per_page = 10

    asc1_desc0 = request.args.get('asc1_desc0')
    col_name = request.args.get('col_name')
    # ==================================================


    # 기사 제목을 검색한 경우
    if search_msg is not None:
        print('검색')
        search_msg_escaped = conn.escape_string(search_msg)

        sql = "SELECT count(*) as total_count FROM ArticleTable WHERE article_title LIKE '%%%s%%'" % search_msg_escaped
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']

        board_search = db_helper.call_search_article(page, per_page, search_msg, asc1_desc0, col_name)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Articles',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)

        return render_template('article_board.html',
                               board_total=board_search,
                               username=username,
                               pagination=pagination,
                               page=page,
                               search_msg=search_msg,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count)



    # 카테고리 목록을 클릭한 경우
    elif sid1 is not None and sid2 is not None:
        print('카테고리')
        sql = "SELECT count(*) as total_count FROM ArticleTable WHERE article_sid1 = %s and article_sid2 = %s" % (sid1, sid2)
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']

        board_total = db_helper.call_article_by_category(page, per_page, asc1_desc0, col_name, sid1, sid2)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Articles',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)

        return render_template('article_board.html',
                               board_total=board_total,
                               username=username,
                               pagination=pagination,
                               page=page,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count)





    else:
        print('전체')
        sql = "SELECT count(*) as total_count FROM ArticleTable"
        cur.execute(sql)
        total_count = cur.fetchone()['total_count']

        # '추가' row 때문에 하나 뺴줘야한다.
        total_count = total_count - 1

        board_total = db_helper.call_every_article(page, per_page, asc1_desc0, col_name)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total_count,
                                record_name='Articles',
                                bs_version=4,
                                alignment='center',
                                show_single_page=True)

        return render_template('article_board.html',
                               board_total=board_total,
                               username=username,
                               pagination=pagination,
                               page=page,
                               asc1_desc0=asc1_desc0,
                               col_name=col_name,
                               sid1_count=sid1_count,
                               sid2_count=sid2_count)






@app.route('/text_board', methods = ['POST', 'GET'])
def text_board():
    print(request.method + '\t' + request.url)
    search_msg = request.args.get('search_msg')

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))

    username = session['username']



    if request.method == 'GET':
        return reload_text_board(search_msg)



    elif request.method == 'POST':

        if request.form['ORIGINAL'] == '' or request.form['CONVERTED'] == '':
            flash('텍스트를 입력해 주세요.','alert-danger')

            id = session['sent_id']
            original_text = db_helper.select_data_from_table_by_id('sent_original', 'SentenceTable', id)

            converted_list = NumberToWord(original_text)
            converted_text = "\n".join(converted_list)

            page = request.args.get('page')

            return render_template('text_edit.html', original_text = original_text, converted_text = converted_text, page = page, username=username)


        id = session['sent_id']

        sent_converted_count = db_helper.select_data_from_table_by_id('sent_converted_count','SentenceTable', id)
        sent_converted_count = sent_converted_count + 1
        db_helper.update_sent_converted_count(sent_converted_count, id)


        if 'ambiguity' in request.form:
            db_helper.update_sent_ambiguity(1, id)
        else:
            db_helper.update_sent_ambiguity(0, id)


        # POST method 인 경우 값을 받아오는 방식
        converted_text = request.form['CONVERTED']


        db_helper.update_sent_converted(converted_text, id)
        db_helper.update_sent_modified_date(id)
        db_helper.update_sent_confirm(id)


        return reload_text_board(search_msg)




@app.route('/article_board', methods = ['GET'])
def article_board():
    print(request.method + '\t' + request.url)
    search_msg = request.args.get('search_msg')

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))


    if request.method == 'GET':
        return reload_article_board(search_msg)
    else:
        return '잘못된 접근'








@app.route('/text_board/edit', methods=['GET'])
def text_edit():


    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))

    username = session['username']


    page = request.args.get('page')
    sent_id = request.args.get('sent_id')
    article_id = request.args.get('article_id')
    search_msg = request.args.get('search_msg')
    session['sent_id'] = sent_id

    print(request.url)
    print('edit page' + str(request.args.get('page')))
    print('article id: ' + str(article_id))


    original_text = db_helper.select_data_from_table_by_id('sent_original', 'SentenceTable', sent_id)

    converted_list = NumberToWord(original_text)
    converted_text = "\n".join(converted_list)


    if search_msg is not None:
        return render_template('text_edit.html', original_text=original_text, converted_text=converted_text, page=page, search_msg=search_msg, article_id=article_id, username=username)
    else:
        return render_template('text_edit.html', original_text = original_text, converted_text = converted_text, page = page, article_id=article_id, username=username)


#@app.route('/<board_type>/delete', methods=['GET'])
@app.route('/<board_type>/delete', methods=['POST'])
def delete(board_type):
    print(request.url)
    print(request.method)

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))


    if board_type == 'article_board':
        # POST method 받아오는 방법
        page = request.form['page']
        article_id = request.form['article_id']

        db_helper.delete_by_id('ArticleTable', article_id)
        return redirect(url_for('article_board', page=page))

    elif board_type == 'text_board':
        # POST method 받아오는 방법
        page = request.form['page']
        sent_id = request.form['sent_id']

        db_helper.delete_by_id('SentenceTable',sent_id)
        return redirect(url_for('text_board', page=page))




@app.route('/text_board/create', methods = ['GET', 'POST'])
def text_create():
    print(request.method)

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))

    username = session['username']

    page = request.args.get('page')


    if request.method == 'GET':
        return render_template('text_create.html', page = page, username=username)



    elif request.method == 'POST':
        if request.form['text_create'] == '':
            flash('텍스트를 입력해주세요.', 'alert-danger')
            return render_template('text_create.html', page = page, username=username)


        added_dict = {}

        # POST 방식으로 보낸 정보 받아오기
        text_create = request.form['text_create']
        print('created text: ' + text_create)


        largest_sent_id = db_helper.select_largest_sent_id()


        added_dict['sent_id'] = largest_sent_id + 1
        added_dict['sent_original'] = text_create

        # 기사로부터 가져온 것이 아니라 새로 추가한 것이기 때문에 1 로 설정, article_id는 0으로 설정
        added_dict['sent_is_added'] = 1
        added_dict['ArticleTable_article_id'] = 0


        db_helper.insert_new_text(added_dict)


        return redirect(url_for('text_board', page = page, username=username))


@app.route('/<board_type>/search', methods=['GET'])
def search(board_type):

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))


    article_id = request.args.get('article_id')
    search_msg = request.args.get('search_msg')
    page = request.args.get('page')


    # 빈 문자열 입력시 모든 Sentence 출력
    if search_msg.strip() == "":
        if board_type == 'article_board':
            return redirect(url_for('article_board', page=page))
        elif board_type == 'text_board':
            return redirect(url_for('text_board', page = page))


    print('article id: ' + str(article_id))
    print("search msg: " + search_msg)
    print("page: " + str(page))


    if board_type == 'article_board':
        return redirect(url_for('article_board', search_msg=search_msg, page=page))
    elif board_type == 'text_board':
        return redirect(url_for('text_board', search_msg=search_msg, page=page, article_id=article_id))




@app.route('/<board_type>/order', methods=['GET'])
def order(board_type):

    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))

    page = request.args.get('page')
    col_name = request.args.get('col_name')
    asc1_desc0 = request.args.get('asc1_desc0')
    search_msg = request.args.get('search_msg')
    article_id = request.args.get('article_id')


    if board_type == 'article_board':
        # 검색한 경우 ordering
        if search_msg is not None:
            return redirect(url_for('article_board', col_name=col_name, asc1_desc0=asc1_desc0, page=page, search_msg=search_msg))
        # 검색하지 않았을 경우 ordering
        else:
            return redirect(url_for('article_board', col_name=col_name, asc1_desc0=asc1_desc0, page=page))

    elif board_type == 'text_board':
        # 검색한 경우 ordering
        if search_msg is not None:
            return redirect(url_for('text_board', col_name = col_name, asc1_desc0 = asc1_desc0, page = page, search_msg=search_msg, article_id=article_id))
        # 검색하지 않았을 경우 ordering
        else:
            return redirect(url_for('text_board', col_name = col_name, asc1_desc0 = asc1_desc0, page = page, article_id=article_id))











# ==================================================================================================================================




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
            #return redirect(url_for('text_board', page = 1, col_name='sent_id', asc1_desc0='1'))
            return redirect(url_for('article_board', page = 1, col_name='article_id', asc1_desc0='1'))
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






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)