import _tqapi
import pandas as pd
import traceback
import threading

def _to_date(row):
    date = int(row['date'])
    return pd.datetime(year=date // 10000, month=date // 100 % 100, day=date % 100)

def _to_datetime(row):
    date = int(row['date'])
    time = int(row['time']) // 1000
    return pd.datetime(year=date // 10000, month=date // 100 % 100, day=date % 100,
                       hour=time // 10000, minute=time // 100 % 100, second=time % 100)
def _add_index(df):
    if 'time' in df.columns:
        df.index = df.apply(_to_datetime, axis=1)
    elif 'date' in df.columns:
        df.index = df.apply(_to_date, axis=1)    
    return df

class TradeApi:
    
    def __init__(self, addr):
        self._handle = _tqapi.tapi_create(addr)
        self._on_order_status   = None
        self._on_order_trade    = None
        self._on_account_status = None

    def __del__(self):
        if self._handle:
            _tqapi.tapi_destroy(self._handle)

    def _on_callback(self, method, data):
        if method == "tapi.order_status_ind":
            if self._on_order_status:
                self._on_order_status(data)

        elif method == "tapi.order_trade_ind":
            if self._on_order_trade:
                self._on_order_trade(data)
            
        elif method == "tapi.account_status_ind":
            if self._on_account_status:
                self._on_account_status(data)

    def set_on_order_status(self, callback):
        """Set on_order_status callback"""
        self._on_order_status = callback
   
    def set_on_order_trade(self, callback):
        """Set on_order_trade callback."""
        self._on_order_trade = callback

    def set_on_account_status(self, callback):
        """Set on_account_status callback"""
        self._on_account_status = callback

    def account_status(self):
        """Get trade account connection status"""
        return _tqapi.tapi_query_account_status(self._handle)

    def query_balance(self, account_id):
        """Get balance of one account."""
        return _tqapi.tapi_query_balance(self._handle, str(account_id))

    def query_trades(self, account_id):
        """Get trades of one account."""
        v, msg = _tqapi.tapi_query_trades(self._handle, str(account_id))
        if v is not None:
            return pd.DataFrame(v), msg
        else:
            return (None, msg)

    def query_orders(self, account_id):
        """Get orders of one account."""
        v, msg = _tqapi.tapi_query_orders(self._handle, str(account_id))
        if v is not None:
            return pd.DataFrame(v), msg
        else:
            return (None, msg)

    def query_positions(self, account_id):
        """Get positions of one account."""
        v, msg = _tqapi.tapi_query_positions(self._handle, str(account_id))
        if v is not None:
            return pd.DataFrame(v), msg
        else:
            return (None, msg)
    
    def place_order(self, account_id, code, price, size, action, order_id=0):
        """Place an order and return entrust_no"""
        return _tqapi.tapi_place_order(self._handle, str(account_id), str(code),
                                       float(price), long(size), str(action), int(order_id))
            
    def cancel_order(self, account_id, code, entrust_no="", order_id=0):
        """Canel order"""
        return _tqapi.tapi_cancel_order(self._handle, account_id, code, entrust_no, order_id)

    def query(self, account_id, command, params=""):
        """common query"""
        return _tqapi.tapi_query(self._handle, str(account_id), str(command), str(params))

class DataApi:
    def __init__(self, addr):
        self._handle = _tqapi.dapi_create(addr)
        self._on_quote = None
        self._on_bar = None
        _tqapi.dapi_set_callback(self._handle, self._on_callback)

    def __del__(self):
        if self._handle:
            _tqapi.dapi_destroy(self._handle)

    def _on_callback(self, method, data):
        try:
            if method == "dapi.quote" :
                if self._on_quote :
                    self._on_quote(data)
            elif method == "dapi.bar" :
                if self._on_bar:
                    self._on_bar(data["cycle"], data["bar"])
        except Exception as e:
            traceback.print_exc()

    def set_on_quote(self, func):
        """Set on_quote callback"""
        self._on_quote = func

    def set_on_bar(self, func):
        """Set on_bar callback"""
        self._on_bar = func

    def subscribe(self, codes) :
        if type(codes) is tuple or type(codes) is list:
            codes = ",".join(codes)

        return _tqapi.dapi_subscribe(self._handle, str(codes) )

    def unsubscribe(self, codes):
        if type(codes) is tuple or type(codes) is list:
            codes = ",".join(codes)            

        return _tqapi.dapi_unsubscribe(self._handle, str(codes))

    #def _my_callback(self, event, id, data):
    #    cb = self._callback_map.get(event)
    #    if cb:
    #        cb(id, data)
    #

    def quote(self, code):
        return _tqapi.dapi_quote(self._handle, str(code))

    def bar(self, code, cycle="1m", trading_day=0, align=True, index=False):
        v, msg = _tqapi.dapi_bar(self._handle, str(code), str(cycle), int(trading_day), bool(align))
        if v:
            df = pd.DataFrame(v)
            if df is not None and index:
                df = _add_index(df)
            return (df, msg)
        else:
            return (v, msg)

    def daily_bar(self, code, price_adj="", align=True, index=False):
        v, msg = _tqapi.dapi_dailybar(self._handle, str(code), str(price_adj), bool(align))
        if v:
            df = pd.DataFrame(v)
            if df is not None and index:
                df = _add_index(df)
            return (df, msg)
        else:
            return (v, msg)

    def tick(self, code, trading_day=0, index=False):
        v, msg = _tqapi.dapi_tick(self._handle, str(code), int(trading_day))
        if v:
            df = pd.DataFrame(v)
            if df is not None and index:
                df = _add_index(df)
            return (df, msg)
        else:
            return (v, msg)

def set_params(key, value):
    _tqapi.set_params(str(key), str(value))
