# encoding: UTF-8
from __future__ import print_function

from .brokerage_base import BrokerageBase
from ..event.event import EventType
from ..order.fill_event import FillEvent
from ..order.order_event import OrderEvent
from ..order.order_status import OrderStatus

class BacktestBrokerage(BrokerageBase):
    """
    Backtest brokerage: order placed will be immediately filled.
    """
    def __init__(self, events_engine, data_board):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.
        """
        self._events_engine = events_engine
        self._data_board = data_board

    # ------------------------------------ private functions -----------------------------#
    def _calculate_commission(self, full_symbol, fill_price, fill_size):
        # take ib commission as example
        if 'STK' in full_symbol:
            commission = max(0.005*abs(fill_size), 1)
        elif 'FUT' in full_symbol:
            commission = 2.01 * abs(fill_size)
        elif 'OPT' in full_symbol:
            commission = max(0.7 * abs(fill_size), 1)
        elif 'CASH' in full_symbol:
            commission = max(0.000002 * abs(fill_price * fill_size), 2)
        else:
            commission = 0

        return commission

    # -------------------------------- end of private functions -----------------------------#

    # -------------------------------------- public functions -------------------------------#
    def place_order(self, order_event):
        """
        immediate fill, no latency or slippage
        """
        ## TODO: acknowledge the order
        order_event.order_status = OrderStatus.FILLED

        fill = FillEvent()
        fill.internal_order_id = order_event.internal_order_id
        fill.broker_order_id = order_event.broker_order_id
        fill.timestamp = self._data_board.get_last_timestamp(order_event.full_symbol)
        fill.full_symbol = order_event.full_symbol
        fill.fill_size = order_event.size
        ## TODO: use bid/ask to fill short/long
        fill.fill_price = self._data_board.get_last_price(order_event.full_symbol)
        fill.exchange = 'BACKTEST'
        fill.commission = self._calculate_commission(fill.full_symbol, fill.fill_price, fill.fill_size)

        self._events_engine.put(fill)

    def cancel_order(self, order_id):
        """cancel order is not supported"""
        pass
    # ------------------------------- end of public functions -----------------------------#
