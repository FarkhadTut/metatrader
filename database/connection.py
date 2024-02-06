import sqlite3
from sqlite3 import Error
import os
from utils.logs import logger
import datetime


class Database():
    def __init__(self) -> None:
        filename = 'metatrader.sqlite3'
        self.db_path = os.path.join('database', filename)
        self.conn = None
        self.closed_by = {'user': 1,
                          'bot': 2}
        self.create_connection()

    def create_connection(self):
        try:
            if os.path.exists(self.db_path):
                self.conn = sqlite3.connect(self.db_path)
                self.cur = self.conn.cursor()
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
                take_profit REAL,
                closed_by INT
            );
            '''
        self.execute(create_query)
    
    def get_orders(self, magic=None):
        if magic is not None:
            sql = """SELECT * FROM ORDERS
                     WHERE magic = (?)
                     """
            result = self.cur.execute(sql, (magic,))
        else:
            sql = """SELECT * FROM ORDERS """
            result = self.cur.execute(sql)

        orders = result.fetchall()
        return orders

    def execute(self, sql):
        self.cur.execute(sql)
        self.conn.commit()


    def fit_request_to_database(self, _request):
        fields = ['magic', 'time_open', \
                  'time_close', 'lot', 
                  'symbol', 'order_type', 
                  'profit', 'price_open', 
                  'price_close', 'stop_loss', 
                  'take_profit']
        
        order_body = {}
        order_body['magic'] = _request['magic']
        order_body['time_open'] = datetime.datetime.now()
        order_body['time_close'] = datetime.datetime.now()
        order_body['lot'] = _request['volume']
        order_body['symbol'] = _request['symbol']
        order_body['order_type'] = _request['type']
        order_body['price_open'] = _request['price']
        order_body['stop_loss'] = _request['sl']
        order_body['take_profit'] = _request['tp']
        order_body['profit'] = None
        order_body['price_close'] = None
        
        return order_body

    def order_exists(self, magic):
        orders = self.get_orders(magic)
        return len(orders) == 1

    def save_close_order(self, _request):
        order_body = self.fit_request_to_database(_request)
 
    

    def save_open_order(self, _request):
        
        order_body = self.fit_request_to_database(_request)
        fields = list(order_body.keys())
        
        insert_query = f'''
            INSERT INTO orders (
                {', '.join(fields)}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data = [order_body[f] for f in fields]
        self.cur.execute(insert_query, data)
        self.conn.commit() 

    def save_order(self, _request):
        magic = _request['magic']
        if self.order_exists(magic):
            self.save_close_order(_request)
        else:
            self.save_open_order(_request)
        

    def close(self):
        self.conn.close()

    
database = Database()
