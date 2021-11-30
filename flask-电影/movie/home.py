from flask import render_template, request, flash, url_for, redirect, Blueprint
from copy import deepcopy
import re, os
from time import sleep
home_blue = Blueprint('home', __name__, template_folder='templates')

from movie import conf


@home_blue.route('/', methods=['GET', 'POST'])
def home():
    temp = deepcopy(conf.videos)
    mark = 0
    dir_ = os.listdir(os.path.dirname(__file__) + '\\static\\movie_image')
    for t in conf.videos:
        count = 0
        for i in t:
            conf.cursor.execute('select id,star,name,year from movie_info where id="%d"' % i)
            info = list(conf.cursor.fetchone())
            for d in dir_:
                mat = re.match('%d\..{2,4}' % info[0], d)
                if mat:
                    info[0] = [info[0], mat.group(0)]
                    break
            info[1] = eval(info[1])[0]
            if info[1] == 0:
                info[1] = '暂无评分'
            temp[mark][count] = info
            count += 1
        mark += 1
    conf.conn.commit()
    return render_template('home.html', videos=temp, lens=[len(temp[0]), len(temp[1])])


