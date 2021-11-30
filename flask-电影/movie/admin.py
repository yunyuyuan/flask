from flask import render_template, request, flash, url_for, redirect, Blueprint, session
from pymysql import escape_string
import os, re
from copy import deepcopy
from time import sleep

admin_blue = Blueprint('admin', __name__, template_folder='templates')
from movie import conf


@admin_blue.route('/', methods=['GET', 'POST'])
def admin():
    if session.get('user_id'):
        return redirect(url_for('admin.menu', item="info"))
    else:
        return render_template(url_for('login'))


@admin_blue.route('/<item>', methods=['GET', 'POST'])
def menu(item):
    # 判断是否登陆
    if not session.get('user_id'):
        return redirect(url_for('login'))
    # 信息
    if item == 'info':
        dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\user_picture\\')
        for i in dir_:
            mat = re.match(str(session['user_id'])+'\..*', i)
            if mat:
                pic = mat.group(0)
                break
        else:
            pic = '0.jpg'
        conf.cursor.execute('select name,sign,number,pwd from movie_users where id="%s"' % session['user_id'])
        info = conf.cursor.fetchone()
        session['user_name'] = info[0]
        session['user_sign'] = info[1]
        session['user_number'] = info[2]
        session['user_pwd'] = info[3]
        conf.conn.commit()
        return render_template('admin.html', active_item=item, user_number=session['user_number'],
                               user_id=session['user_id'], user_name=session['user_name'],
                               user_collection=session['user_collection'], user_sign=session['user_sign'],
                               user_pwd=session['user_pwd'], user_pic=pic)
    # 修改信息
    elif item == 'modify-info':
        name = request.form['name']
        sign = request.form['sign']
        pwd = request.form['pwd']
        try:
            img = request.files['img']
        except KeyError:
            img = '0'
        if not name or not sign or not pwd:
            pass
        else:
            if img != '0':
                # 删除
                dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\user_picture\\')
                for i in dir_:
                    m = re.match(str(session['user_id']) + '\..*', i)
                    if m:
                        os.remove(os.path.dirname(__file__) + '\\static\\user_picture\\' + m.group(0))
                # 存储头像
                base_path = os.path.dirname(__file__)
                upload_image_path = base_path + '\\static\\user_picture\\' + str(session['user_id']) + re.sub('.*?(\..{2,4})$', '\\1', img.filename)
                img.save(upload_image_path)
            conf.cursor.execute('update movie_users set name="%s",sign="%s",pwd="%s" where id="%s"' % (name, sign, pwd, session['user_id']))
            conf.conn.commit()
        return redirect(url_for('admin.menu', item='info'))
    # 上传
    elif item == 'upload':
        if request.method == 'POST':
            # 电影信息传到数据库
            name = request.form['name']
            year = request.form['year']
            summary = request.form['summary']
            if not summary:
                summary = '暂无简介'
            tag = str(request.form['tag'].split('#')[1:])
            conf.cursor.execute(
                'insert into movie_info (name, year, summary, star, comment, give_star, tag) values ('
                '"%s", "%s", "%s", "[0,0]", "[]", "[]", "%s")' % (
                 escape_string(name), escape_string(year), escape_string(summary), escape_string(tag)))
            conf.conn.commit()
            # 取出电影id
            conf.cursor.execute('select @@IDENTITY')
            video_id = conf.cursor.fetchone()[0]

            video_file = request.files['video']
            image_file = request.files['jpg']
            # 上传电影文件和图片文件
            base_path = os.path.dirname(__file__)
            upload_video_path = base_path + '\\static\\video\\' + str(video_id) + re.sub('.*?(\..{2,4})$', '\\1', video_file.filename)
            upload_image_path = base_path + '\\static\\movie_image\\' + str(video_id) + re.sub('.*?(\..{2,4})$', '\\1', image_file.filename)
            video_file.save(upload_video_path)
            image_file.save(upload_image_path)
        return render_template('admin.html', active_item=item, user_id=session['user_id'])
    # 管理收藏
    elif item == 'collection':
        conf.cursor.execute('select collection from movie_users where id="%s"' % session['user_id'])
        all_collection = eval(conf.cursor.fetchone()[0])
        session['collections'] = all_collection
        temp = []
        # 取出电影信息
        for i in all_collection:
            conf.cursor.execute('select id,name,tag from movie_info where id="%s"' % str(i))
            temp.append(conf.cursor.fetchone())
        return render_template('admin.html', active_item=item, user_id=session['user_id'], all_collection=temp)
    # 管理用户
    elif item == 'users':
        conf.cursor.execute('select id,name,number,online from movie_users')
        all_info = conf.cursor.fetchall()
        return render_template('admin.html', active_item=item, user_id=session['user_id'], all_users=all_info)
    # 管理电影
    elif item == 'movies':
        conf.cursor.execute('select id,name,tag from movie_info')
        all_movies = list(conf.cursor.fetchall())
        c = 0
        for i in all_movies:
            all_movies[c] = list(i)
            c += 1
        for i in all_movies:
            i[2] = '|'.join(eval(i[2]))
        return render_template('admin.html', active_item=item, user_id=session['user_id'], all_movies=all_movies)
    elif request.method == 'POST' and item[0:11] == 'collect_id:':
        # 删除收藏
        new_collect = deepcopy(session['collections'])
        new_collect.remove(int(item[11:]))
        conf.cursor.execute('update movie_users set collection="%s" where id="%s"' % (str(new_collect), session['user_id']))
        conf.conn.commit()
        return 'ok'
    elif request.method == 'POST' and item[0:3] == 'id:':
        # 删除用户
        conf.cursor.execute('delete from movie_users where id="%s"' % item[3:])
        conf.conn.commit()
        return 'ok'
    elif request.method == 'POST' and item[0:9] == 'movie-id:':
        # 删除电影mp4
        dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\video\\')
        for i in dir_:
            m = re.match(str(item[9:]) + '\..*', i)
            if m:
                os.remove(os.path.dirname(__file__) + '\\static\\video\\' + m.group(0))
        # 删除电影封面
        dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\movie_image\\')
        for i in dir_:
            m = re.match(str(item[9:]) + '\..*', i)
            if m:
                os.remove(os.path.dirname(__file__) + '\\static\\movie_image\\' + m.group(0))
        # 删除用户的收藏
        conf.cursor.execute('select id,collection from movie_users')
        all_user = list(conf.cursor.fetchall())
        for user in all_user:
            user = list(user)
            user[1] = eval(user[1])
            # 删除该用户的这个收藏
            if int(item[9:]) in user[1]:
                user[1].remove(int(item[9:]))
                conf.cursor.execute('update movie_users set collection="%s" where id="%s"' % (user[1], user[0]))
        # 删除数据库记录
        conf.cursor.execute('delete from movie_info where id="%s"' % item[9:])
        conf.conn.commit()
        return 'ok'
    elif request.method == 'POST' and item[0:8] == 'get-info':
        # 查询电影信息
        conf.cursor.execute('select id,name,tag,summary,year from movie_info where id="%s"' % item[8:])
        movie_info = list(conf.cursor.fetchall())
        c = 0
        for i in movie_info:
            movie_info[c] = list(i)
            c += 1
        for i in movie_info:
            i[2] = '#'+'#'.join(eval(i[2]))
        conf.conn.commit()
        return
    elif request.method == 'POST' and item[0:9] == 'modify-id:':
        # 修改电影
        pass
    return render_template('404.html')



