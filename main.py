
import MetaTrader5 as mt5
from mtrader.data.handler import load_data
from mtrader.action.orders import OrderRequest
from mtrader.account.connection import establish_connection



 
establish_connection()
# get data on MetaTrader 5 version
df = load_data()


magic = 123123
order_request = OrderRequest(
    action='trade',
    type='buy',
    magic=magic,
    )

print(order_request)
result = order_request.send_order()
# shut down connection to MetaTrader 5
mt5.shutdown()
