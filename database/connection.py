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
                position_id INT NOT NULL,
                magic INTEGER NOT NULL,
                time_open DATETIME NOT NULL,
                time_close DATETIME,
                lot REAL NOT NULL,
                point INT NOT NULL,
                symbol TEXT NOT NULL,
                order_type INTEGER NOT NULL,
                price_open REAL NOT NULL,
                price_close REAL,
                stop_loss REAL,
                take_profit REAL,
                closed_by INT
            );
            '''
        self.execute(create_query)
    
    def get_order_by_pid(self, position_id):
      
        sql = """SELECT * FROM orders
                    WHERE position_id = (?)
                    """
        result = self.cur.execute(sql, (position_id,))
        orders = result.fetchall()
        if len(orders) == 0:
            return 
        return orders[0]

    def execute(self, sql, data=None):
        try:
            if data is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, data)
            self.conn.commit()
            return True
        except Exception as e:
            command = sql.split(" ")[0] 
            logger.error(f'In {command} query. {e}')
            return False


    def fit_request_to_database(self, _request):
        fields = ['magic', 'time_open', \
                  'time_close', 'lot', 
                  'symbol', 'order_type', 
                  'profit', 'price_open', 
                  'price_close', 'stop_loss', 
                  'take_profit']
        
        order_body = {}
        order_body['magic'] = _request['magic']
        order_body['position_id'] = _request['position_id']
        order_body['time_open'] = datetime.datetime.now()
        order_body['time_close'] = datetime.datetime.now()
        order_body['lot'] = _request['volume']
        order_body['point'] = _request['point']
        order_body['symbol'] = _request['symbol']
        order_body['order_type'] = _request['type']
        order_body['price_open'] = _request['price']
        order_body['stop_loss'] = _request['sl']
        order_body['take_profit'] = _request['tp']
        order_body['price_close'] = None
        
        return order_body

    def order_exists(self, position_id):
        order = self.get_order_by_pid(position_id)
        if order is None:
            logger.error(f"Order with position_id={position_id} not found in database.")
        return True

    def magic_exists(self, magic):
        check_magic_query = """ SELECT COUNT(*) FROM orders WHERE magic=? """
        data = (magic,)
        result = self.cur.execute(check_magic_query, data)
        orders_count = result.fetchall()[0][0]
        return orders_count > 0

    def save_close(self, position_id, price_close):
        if self.order_exists(position_id):
            closed_by = 'bot'
            save_close_query = """
                UPDATE orders 
                SET price_close=?, closed_by=?  
                WHERE position_id=?
            """
            data = (price_close, closed_by, position_id)    
            result = self.execute(save_close_query, data)
            return result
        return False
 
    

    def save_open_order(self, _request):
        
        order_body = self.fit_request_to_database(_request)
        fields = list(order_body.keys())
        
        insert_query = f'''
            INSERT INTO orders (
                {', '.join(fields)}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data = [order_body[f] for f in fields]
        self.cur.execute(insert_query, data)
        self.conn.commit() 

    def save_open(self, _request):
        position_id = _request['position_id']
        self.save_open_order(_request)
        

    def close(self):
        self.conn.close()

    
database = Database()
