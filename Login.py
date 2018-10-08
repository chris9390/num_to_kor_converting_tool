from flask import Flask, request, session, render_template, redirect, url_for, flash, g
from flask_bootstrap import Bootstrap
import flask_login
import hashlib
import pymysql
import os
from db_helper import DB_Helper
from flask_paginate import Pagination
from NumberToWord import *
from datetime import timedelta


app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(24)
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)




# 사용자 클래스
class user_class:
    def __init__(self, user_id, pw_hash=None, authenticated=False):
        self.user_id = user_id
        self.pw_hash = pw_hash
        self.authenticated = authenticated

    def can_login(self, pw_hash):
        return self.pw_hash == pw_hash

    def is_active(self):
        return True

    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    @classmethod
    def get(cls, user_id):
        pw_hash = users[user_id].pw_hash
        return cls(user_id, pw_hash)



login_manager = flask_login.LoginManager()
login_manager.init_app(app)


sid1_count = {'정치' : 0, '경제' : 0, '사회' : 0, '생활/문화' : 0, '세계' : 0, 'IT/과학' : 0}

sid2_count = {'청와대' : 0, '국회/정당' : 0, '북한' : 0, '행정' : 0, '국방/외교' : 0, '정치 일반' : 0,
              '금융' : 0, '증권' : 0, '산업/재계' : 0, '중기/벤처' : 0, '부동산' : 0, '글로벌 경제' : 0, '생활 경제' : 0, '경제 일반' : 0,
              '사건사고' : 0, '교육' : 0, '노동' : 0, '언론' : 0, '환경' : 0, '인권/복지' : 0, '식품/의료' : 0, '지역' : 0, '인물' : 0, '사회 일반' : 0,
              '건강정보' : 0, '자동차/시승기' : 0, '도로/교통' : 0, '여행/레저' : 0, '음식/맛집' : 0, '패션/뷰티' : 0, '공연/전시' : 0, '책' : 0, '종교' : 0, '날씨' : 0, '생활문화 일반' : 0,
              '아시아/호주' : 0, '미국/중남미' : 0, '유럽' : 0, '중동/아프리카' : 0, '세계 일반' : 0,
              '모바일' : 0, '인터넷/SNS' : 0, '통신/뉴미디어' : 0, 'IT 일반' : 0, '보안/해킹' : 0, '컴퓨터' : 0, '게임/리뷰' : 0, '과학 일반' : 0}


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = pymysql.connect(host='163.239.169.54',
                             port=3306,
                             user='s20131533',
                             passwd='s20131533',
                             db='number_to_word',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
        g._database = db
    else:
        db.ping()

    return db



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@login_manager.user_loader
def user_loader(user_id):
     return user_class.get(user_id)


@app.route('/logout')
@flask_login.login_required
def logout():
    # session['logged_in'] = False
    # session.pop('username', None)
    # session.pop('password', None)

    user = flask_login.current_user
    user.authenticated = False
    flask_login.logout_user()

    flash('로그아웃 되었습니다.', 'alert-success')
    #return redirect(url_for('login'))
    return render_template('login_form.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login_form.html')


@app.route('/login_check', methods=['POST', 'GET'])
def login_check():
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    if request.method == 'POST':

        global users
        users = {}

        # DB에 저장된 user 정보 받아와서 users 딕셔너리에 저장
        rows = db_helper.select_every_rows_from_table('user_info')
        for row in rows:
            users[row['username']] = user_class(row['username'], pw_hash=row['password'])


        user_id = request.form['username']
        pw = request.form['password']

        # 비밀번호 인코딩
        pw = pw.encode('utf-8')

        # 비밀번호에 해시함수 적용
        pw_hash = hashlib.sha512(pw).hexdigest()

        # 유저이름과 그에 해당하는 패스워드가 일치하는지 확인
        if users[user_id].can_login(pw_hash):

            # session['logged_in'] = True
            # session['username'] = request.form['username']
            # session['password'] = request.form['password']

            users[user_id].authenticated = True
            flask_login.login_user(users[user_id])
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=6)

            return redirect(url_for('article_board', page=1, col_name='article_id', asc1_desc0='1'))

        else:
            error_msg = '로그인 정보가 맞지 않습니다.'
            flash(error_msg, 'alert-danger')
            return render_template('login_form.html')


    elif request.method == 'GET':
        #return redirect(url_for('login'))
        return render_template('login_form.html')



@login_manager.unauthorized_handler
def unauthorized():
    flash('자동 로그아웃 되었습니다. 다시 로그인 해주세요.', 'alert-danger')
    return render_template('login_form.html')


# ===================================================================================================================
# ===================================================================================================================
# ===================================================================================================================


def reload_text_board(search_msg):
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    username = flask_login.current_user.user_id


    sid1 = None
    sid2 = None
    article_id = request.args.get('article_id')
    if (article_id is not None) and (article_id != 'None'):
        sid1 = db_helper.select_data_from_table_by_id('article_sid1', 'ArticleTable', article_id)
        sid2 = db_helper.select_data_from_table_by_id('article_sid2', 'ArticleTable', article_id)
    #sid1 = request.args.get('sid1')
    #sid2 = request.args.get('sid2')


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

        search_msg_escaped = db_conn.escape_string(search_msg)
        total_count = db_helper.total_count_text_search(search_msg_escaped)

        article_title = None
        if (article_id is not None) and (article_id != 'None'):
            article_title = db_helper.select_data_from_table_by_id('article_title', 'ArticleTable', article_id)


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
                               article_title=article_title,
                               article_id=article_id,
                               article_board_page=article_board_page,
                               sid1=sid1,
                               sid2=sid2)


    # 특정 기사를 클릭한 경우
    elif article_id is not None:
        print('특정 기사 클릭')

        total_count = db_helper.total_count_clicked_article(article_id)
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
                               article_board_page=article_board_page,
                               sid1=sid1,
                               sid2=sid2)



    # 게시글 전체 반환
    else:
        print('전체')
        total_count = db_helper.total_count_every_sentences()
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
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    username = flask_login.current_user.user_id

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
        search_msg_escaped = db_conn.escape_string(search_msg)
        total_count = db_helper.total_count_article_search(search_msg_escaped)

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
    elif (sid1 is not None and sid2 is not None) and (sid1 != '' and sid2 != ''):
        print('카테고리')
        total_count = db_helper.total_count_article_category(sid1, sid2)
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
                               sid2_count=sid2_count,
                               sid1=sid1,
                               sid2=sid2)





    else:
        print('전체')
        total_count = db_helper.total_count_every_articles()

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
@flask_login.login_required
def text_board():
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    print(request.method + '\t' + request.url)
    search_msg = request.args.get('search_msg')


    username = flask_login.current_user.user_id




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
        converted_text_escaped = db_conn.escape_string(converted_text)

        db_helper.update_sent_converted(converted_text_escaped, id)
        db_helper.update_sent_modified_date(id)
        db_helper.update_sent_confirm(id)


        return reload_text_board(search_msg)




@app.route('/article_board', methods = ['GET'])
@flask_login.login_required
def article_board():
    print(request.method + '\t' + request.url)
    search_msg = request.args.get('search_msg')


    if request.method == 'GET':
        return reload_article_board(search_msg)
    else:
        return '잘못된 접근'








@app.route('/text_board/edit', methods=['GET'])
@flask_login.login_required
def text_edit():
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    '''
    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))
    '''

    #username = session['username']
    username = flask_login.current_user.user_id

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
@flask_login.login_required
def delete(board_type):
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    print(request.url)
    print(request.method)

    '''
    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))
    '''

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
@flask_login.login_required
def text_create():
    db_conn = get_db()
    db_helper = DB_Helper(db_conn)

    print(request.method)

    '''
    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))
    '''

    #username = session['username']
    username = flask_login.current_user.user_id

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
@flask_login.login_required
def search(board_type):

    article_id = request.args.get('article_id')
    search_msg = request.args.get('search_msg')
    page = request.args.get('page')
    sid1 = request.args.get('sid1')
    sid2 = request.args.get('sid2')



    # 빈 문자열 입력시 에러
    if search_msg.strip() == "":
        flash('1글자 이상 써주십시오.','alert-danger')

        if board_type == 'article_board':
            return redirect(url_for('article_board', sid1=sid1, sid2=sid2))

        elif board_type == 'text_board':
            return redirect(url_for('text_board', article_id=article_id))


    print("article id: " + str(article_id))
    print("search msg: " + search_msg)
    print("page: " + str(page))


    if board_type == 'article_board':
        return redirect(url_for('article_board', search_msg=search_msg, page=page))
    elif board_type == 'text_board':
        return redirect(url_for('text_board', search_msg=search_msg, page=page, article_id=article_id))




@app.route('/<board_type>/order', methods=['GET'])
@flask_login.login_required
def order(board_type):

    '''
    # 로그인된 상태가 아니라면 로그인 페이지로 이동
    if 'username' not in session.keys():
        flash('로그인 해주세요.', 'alert-danger')
        return redirect(url_for('login'))
    '''

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






'''
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
'''





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)