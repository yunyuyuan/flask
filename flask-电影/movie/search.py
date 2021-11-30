from flask import render_template, request, flash, url_for, redirect, Blueprint, session
import os, re

search_blue = Blueprint('search', __name__, template_folder='templates')
from movie import conf
from time import sleep

@search_blue.route('/', methods=['GET', 'POST'])
def search():
    return render_template('search.html')


@search_blue.route('/<tags>', methods=['POST', 'GET'])
def get_search(tags):
    if request.method == 'POST':
        # 返回电影总数
        if tags == 'all':
            return str(len(session['search_temp']))
        # 没发内容过来
        elif tags == '[':
            return '1'
        # 返回第一页电影
        elif tags[0] == '[':
            tags = tags[1:]
            conf.cursor.execute('select name,id,tag,year from movie_info where name like "%s"' % ('%' + tags + '%'))
            all_movie = list(conf.cursor.fetchall())
            temp = []
            dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\movie_image')
            for one_movie in all_movie:
                info = list(one_movie)
                for i in dir_:
                    mat = re.match('%d\..{2,4}' % info[1], i)
                    if mat:
                        info[1] = mat.group(0)
                        break
                info[2] = eval(info[2])
                temp.append(info)
            # 保存搜索到的电影数据到session
            session['search_temp'] = temp
            t = temp[0:6]
            # 转化为字符串
            if t:
                s = ""
                for item in t:
                    for i in item:
                        s += (str(i) + '|')
                return s
            # 没搜到电影
            else:
                return '0'
        # 返回某页电影
        else:
            page = int(tags) - 1
            t = session['search_temp'][page*6:page*6+6]
            # 转化为字符串
            s = ""
            for item in t:
                for i in item:
                    s += (str(i) + '|')
            return s
    return render_template('404.html')


