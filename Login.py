from flask import Flask, request, session, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from NumberToWord import *


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'abc'


@app.route('/main')
def main():
    if 'username' in session.keys() and 'password' in session.keys():
        return session['username'] + '님 로그인을 환영합니다.'
    else:
        return '로그인 하십시오.'

@app.route('/user/<username>')
def show_user_profile(username):
    return 'User is %s' %username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post id is %d' %post_id

@app.route('/logging')
def logging_test():
    test = 1
    app.logger.debug('디버깅 필요')
    app.logger.warning(str(test) + " 라인")
    app.logger.error('에러발생')
    return "로깅 끝"

@app.route('/login_form')
def login_form():
    return render_template('login_form.html')


@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'chris' and request.form['password'] == '1234':
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            #return request.form['username'] + ' 님 환영합니다.'
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
        print(type(session['input']))
        input_str = session['input']

        output_list = NumberToWord(input)
        output_str = "\n".join(output_list)

        return render_template('main_page.html', input=input_str, output=output_str)
    else:
        return '잘못된 접근'


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('main'))





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)