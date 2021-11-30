# from conf import Config
# conf = Config()
#
# conn = conf.conn
# cursor = conf.cursor
# for i in range(30):
#     cursor.execute('insert into movie_info (name, year, summary, star, comment, give_star, tag) values ("虫师7", "2014", "暂无简介", "[]", "[]", "[]", "[\'剧情\', \'奇幻\', \'动画\']")')
# conn.commit()
import PIL.Image as im

i = im.open('./static/movie_image/33.jpg')
size = i.size
for i in range(30):
    n = im.new("RGB", size)
    n.paste(i, (100, 100, 100, 100))
    n.save('./static/movie_image/%d.jpg' % (i+34))
