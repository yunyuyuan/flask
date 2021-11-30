from flask import Flask
# 数据库连接
from conf import Config
conf = Config()
from movie.home import home_blue
from movie.admin import admin_blue
from movie.search import search_blue
from movie.sort import sort_blue
from movie.play import play_blue

app = Flask(__name__)
from datetime import timedelta
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

app.register_blueprint(home_blue, url_prefix='/home')
app.register_blueprint(sort_blue, url_prefix='/sort')
app.register_blueprint(search_blue, url_prefix='/search')
app.register_blueprint(admin_blue, url_prefix='/admin')
app.register_blueprint(play_blue, url_prefix='/play')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
import movie.login

