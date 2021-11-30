from pymysql import connect

host = '127.0.0.1'


class Config(object):
    def __init__(self):
        self.conn = connect(
            'server.natappfree.cc',
            # '127.0.0.1',
            'root',
            '1607439239',
            'mystorage',
            port=46462,
            charset='utf8mb4',
        )
        self.cursor = self.conn.cursor()
        self.videos = [[67, 68, 69, 70, 71, 72, 73, 74, 75], [85, 82, 67, 68, 69, 70, 71, 72]]

