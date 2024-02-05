import sqlite3
from sqlite3 import Error
import os
from utils.logs import logger
import datetime


class Database():
    def __init__(self) -> None:
        filename = 'metatrader.sqlite3'
        self.db_path = os.path.join('database', filename)
        self.create_connection()
        self.conn = None

    def create_connection(self):
        try:
            if os.path.exists(self.db_path):
                self.conn = sqlite3.connect(self.db_path)
                self.cur = self.conn.cursor
            else:
                self.conn = sqlite3.connect(self.db_path)
                self.cur = self.conn.cursor()
                self.create_table()

            logger.debug(f'SQLite: {sqlite3.version}')
            return True
        except Error as e:
            logger.error(str(e))
            exit()

    def create_table(self):
        create_query = '''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                magic INTEGER NOT NULL,
                time_open DATETIME NOT NULL,
                time_close DATETIME,
                lot REAL NOT NULL,
                symbol TEXT NOT NULL,
                order_type INTEGER NOT NULL,
                profit REAL,
                price_open REAL NOT NULL,
                price_close REAL,
                stop_loss REAL,
                take_profit REAL
            );
            '''
        self.execute(create_query)
    
    def execute(self, sql, data=None):
        if data is not None:
            self.cur.execute(sql, data)
        else:
            self.cur.execute(sql)
        self.conn.commit()

    def fit_request_to_database(self, _request):
        pass

    def save_order(self, _request):
        _request = self.fit_request_to_database(self, _request)
        fields = ['magic', 'time_open', \
                  'time_close', 'lot', 
                  'symbol', 'order_type', 
                  'profit', 'price_open', 
                  'price_close', 'stop_loss', 
                  'take_profit']
        
        insert_query = f'''
            INSERT INTO orders (
                {', '.join(fields)}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data = [_request[f] for f in fields]
        self.execute(insert_query, data)

    def close(self):
        self.conn.close()

    
database = Database()
