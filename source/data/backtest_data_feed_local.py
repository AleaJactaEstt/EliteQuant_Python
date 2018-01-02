#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pandas as pd
from datetime import datetime, timedelta

from .data_feed_base import DataFeedBase
from .bar_event import BarEvent

class BacktestDataFeedLocal(DataFeedBase):
    """
    BacktestDataFeed retrieves historical data; which is pulled out by backtest_event_engine.
    """
    def __init__(
        self, hist_dir=None, start_date=None, end_date=None
    ):
        """
        events_queue receives feed of tick/bar events
        """
        self._hist_dir = hist_dir

        if end_date is not None:
            self._end_date = end_date
        else:
            self._end_date = datetime.today()
        if start_date is not None:
            self._start_date = start_date
        else:
            self._start_date = self._end_date- timedelta(days = 365)

        self._hist_data = {}        # It holds historical data

    # ------------------------------------ private functions -----------------------------#
    def _retrieve_historical_data(self, symbol):
        """
        Retrieve historical data from web
        """
        hist_file = os.path.join(self._hist_dir, "%s.csv" % symbol)

        data = pd.io.parsers.read_csv(
            hist_file, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Close", "Adj Close", "Volume"
            )
        )

        start_idx = data.index.searchsorted(self._start_date)
        end_idx = data.index.searchsorted(self._end_date)
        data = data.ix[start_idx:end_idx]

        self._hist_data[symbol] = data
        self._hist_data[symbol]["FullSymbol"] = symbol         # attach symbol to data; it will be merged into _data_stream

    def _retrieve_local_historcial_data(self, symbol):
        """ TODO """
        pass

    # -------------------------------- end of private functions -----------------------------#

    # ------------------------------------ public functions -----------------------------#
    def subscribe_market_data(self, symbols):
        if symbols is not None:
            for sym in symbols:
                self._retrieve_historical_data(sym)       # retrieve historical data

        # merge sort data into stream
        df = pd.concat(self._hist_data.values()).sort_index()
        self._data_stream = df.iterrows()

    def unsubscribe_market_data(self, symbols):
        pass

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        index, row = next(self._data_stream)

        # Obtain all elements of the bar from the dataframe
        b = BarEvent()
        b.bar_start_time = index
        b.interval = 86400
        b.full_symbol = row["FullSymbol"]
        b.open_price = row["Open"]
        b.high_price = row["High"]
        b.low_price = row["Low"]
        b.close_price = row["Close"]
        b.adj_close_price = row["Adj Close"]
        b.volume = int(row["Volume"])

        return b
    # ------------------------------- end of public functions -----------------------------#