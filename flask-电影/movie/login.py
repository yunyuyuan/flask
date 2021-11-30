from movie import app
from flask import render_template, request, flash, url_for, redirect, session
# from time import sleep
from movie import conf
from time import sleep


@app.route('/')
def skip():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        number = request.form['number']
        pwd = request.form['password']
        session['user_number'] = number
        conf.cursor.execute('select id,name,collection,sign,pwd,online from movie_users where number="%s" and pwd="%s"' % (number, pwd))
        user_info = conf.cursor.fetchone()
        if not user_info:
            flash("用户名或密码错误！")
        # elif user_info[-1] == '1':
        #     flash("该用户已经在线！若密码被盗，请联系管理员")
        else:
            # flash("登陆成功！")
            # sleep(1)
            session['user_id'] = user_info[0]
            session['user_name'] = user_info[1]
            session['user_collection'] = user_info[2]
            session['user_sign'] = user_info[3]
            session['user_pwd'] = user_info[4]
            # 置状态为在线
            conf.cursor.execute('update movie_users set online=1  where id="%s"' % session['user_id'])
            return redirect(url_for('admin.admin'))
    else:
        try:
            id_ = session['user_id']
            # 置状态为离线
            conf.cursor.execute('update movie_users set online=0  where id="%s"' % id_)
            session.clear()
        except KeyError:
            pass
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        pwd = request.form['password']
        c_pwd = request.form['certain-password']
        if not name or not number or not pwd or not c_pwd:
            flash('请输入完整信息！', 'error')
        else:
            if pwd != c_pwd:
                flash('两次密码不一致！', 'error')
            elif len(number) > 11:
                flash('账号过长！')
            else:
                conf.cursor.execute('select id from movie_users where number = "%s"' % number)
                if conf.cursor.fetchone():
                    flash('手机号/账号 已经存在！', 'error')
                else:
                    conf.cursor.execute('insert into movie_users(name, number, pwd, collection, sign,online) '
                                   'values("%s", "%s", "%s", "[]", "none", "0")' % (name, number, pwd))
                    conf.conn.commit()
                    return redirect(url_for('login'))
    return render_template('register.html')
