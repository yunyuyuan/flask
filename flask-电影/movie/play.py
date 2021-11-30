from flask import render_template, request, flash, url_for, redirect, Blueprint, session
import re, os
from copy import deepcopy
from time import sleep

play_blue = Blueprint('play', __name__, template_folder='templates')
from movie import conf


def get_im_name():
    conf.cursor.execute('select comment from movie_info where id="%s"' % session['video_id'])
    new_comments = eval(conf.cursor.fetchone()[0])
    # 取出所有id
    ids = list(set([x[1] for x in new_comments]))
    for i in range(len(ids)):
        conf.cursor.execute('select name from movie_users where id="%s"' % ids[i])
        name = conf.cursor.fetchone()[0]
        # 获取头像文件后缀
        dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\user_picture')
        for d in dir_:
            mat = re.match('%s\..{2,4}' % ids[i], d)
            if mat:
                file_name = mat.group(0)
                break
        ids[i] = [ids[i], name, file_name]
    for item in range(len(new_comments)):
        for i in range(len(ids)):
            if str(new_comments[item][1]) == str(ids[i][0]):
                new_comments[item].pop()
                new_comments[item].extend(ids[i])
                break
    return new_comments


@play_blue.route('/', methods=['GET', 'POST'])
def _play():
    if request.method == 'POST':
        return redirect(url_for('play.play', video_id=session['video_id']))
    else:
        return render_template('404.html')


@play_blue.route('/<video_id>', methods=['POST', 'GET'])
def play(video_id):
    if request.method == 'POST':
        # 修改评分
        if video_id[0:6] == 'modify':
            give_star = float(video_id[6:])
            star = [round((session['star'][0] * session['star'][1] + give_star) / (session['star'][1] + 1), 1),
                    session['star'][1] + 1]
            session['give_star'].append(int(session['user_id']))
            conf.cursor.execute('update movie_info set star="%s",give_star="%s" where id="%d"' % (star, session['give_star'], int(session['video_id'])))
            conf.conn.commit()
            for i in range(len(star)):
                star[i] = str(star[i])
            return '|'.join(star)
        # 添加收藏
        elif video_id[0:7] == 'col-id:':
            conf.cursor.execute('select collection from movie_users where id="%s"' % session['user_id'])
            new_collect = eval(conf.cursor.fetchone()[0])
            new_collect.append(int(session['video_id']))
            conf.cursor.execute(
                'update movie_users set collection="%s" where id="%s"' % (str(new_collect), session['user_id']))
            conf.conn.commit()
            return 'ok'
        # 取消收藏
        elif video_id[0:7] == 'rem-id:':
            conf.cursor.execute('select collection from movie_users where id="%s"' % session['user_id'])
            new_collect = eval(conf.cursor.fetchone()[0])
            new_collect.remove(int(session['video_id']))
            conf.cursor.execute(
                'update movie_users set collection="%s" where id="%s"' % (str(new_collect), session['user_id']))
            conf.conn.commit()
            return 'ok'
        # 提交评论
        elif video_id[0:13] == 'give-comment:':
            old_comment = deepcopy(session['comment'])
            # 旧评论加一条
            old_comment.append([video_id[13:], session['user_id']])
            session['comment'] = old_comment
            conf.cursor.execute('update movie_info set comment="%s" where id="%s"' % (str(old_comment), session['video_id']))
            conf.conn.commit()
            new_comments = get_im_name()
            s = ''
            for item in new_comments:
                for i in item:
                    s += str(i)+'|'
            return s
        # 删除评论
        elif video_id[0:10] == 'del_index:':
            old_comment = deepcopy(session['comment'])
            # 评论删除索引
            print(video_id[10:])
            old_comment.pop(int(video_id[10:]))
            session['comment'] = old_comment
            conf.cursor.execute(
                'update movie_info set comment="%s" where id="%s"' % (str(old_comment), session['video_id']))
            conf.conn.commit()
            new_comments = get_im_name()
            s = ''
            for item in new_comments:
                for i in item:
                    s += str(i) + '|'
            return s
    # 验证是否登陆
    if not session.get('user_id'):
        return render_template('404.html')
    # 获取文件后缀
    dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\video')
    for d in dir_:
        mat = re.match('%s\..{2,4}' % video_id, d)
        if mat:
            file_name = mat.group(0)
            break
    else:
        return render_template('404.html')
    conf.cursor.execute('select name,year,star,give_star,summary,comment from movie_info where id="%s"' % video_id)
    infos = conf.cursor.fetchone()
    # 读取电影信息到session
    [name, year, star, give_star, summary, comment] = infos
    star = eval(star)
    give_star = eval(give_star)
    session['video_id'] = video_id
    session['star'] = star
    session['give_star'] = give_star
    if session['user_id'] not in give_star:
        give_star = None
    comment = eval(comment)
    new_comments = get_im_name()
    session['comment'] = comment
    conf.cursor.execute('select collection from movie_users where id="%s"' % session['user_id'])
    coll = eval(conf.cursor.fetchone()[0])
    if int(video_id) in coll:
        is_coll = 1
    else:
        is_coll = 0
    conf.conn.commit()
    return render_template('play.html', file_name=file_name, name=name, id=video_id, year=year, star=star, give_star=give_star, summary=summary,
                           comments=new_comments, len_com=len(new_comments), is_coll=is_coll, user_id=session['user_id'])




