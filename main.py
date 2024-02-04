
import MetaTrader5 as mt5
from mtrader.data.handler import load_data
from config.settings import (
    max_ticks, 
    lot,
    symbol,
    ) 
from mtrader.action.orders import OrderRequest
from mtrader.account.connection import establish_connection



 
establish_connection()
# get data on MetaTrader 5 version
df = load_data(max_ticks())


magic = 123123
order_request = OrderRequest(
    action='trade',
    symbol=symbol(),
    volume=lot(),
    type='buy',
    magic=magic,
    )

result = order_request.send_order()
# shut down connection to MetaTrader 5
mt5.shutdown()
