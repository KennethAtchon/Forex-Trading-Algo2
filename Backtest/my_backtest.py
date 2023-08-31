import datetime
import backtrader as bt

class SMACrossoverStrategy(bt.Strategy):
    params = (
        ("fast", 10),
        ("slow", 30)
    )

    def __init__(self):
        self.dataclose = self.data.close
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.fast)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if self.crossover > 0:
            
            print(self.buy())
        elif self.crossover < 0:
            self.sell()


class SMAStrategy(bt.Strategy):
    params = (
        ("sma_period", 10),  # Period for the moving average
    )

    def __init__(self):
        self.dataclose = self.data.close
        self.sma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.params.sma_period)

    def next(self):
        if self.dataclose[0] > self.sma[0]:
            self.buy()
        elif self.dataclose[0] < self.sma[0]:
            self.sell()

class EMACrossoverStrategy(bt.Strategy):
    params = (
        ("short_period", 10),  # Short-term EMA period
        ("long_period", 20),   # Long-term EMA period
    )

    def __init__(self):
        self.short_ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.short_period)
        self.long_ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if self.short_ema[0] > self.long_ema[0] and self.short_ema[-1] <= self.long_ema[-1]:
            self.buy()
        elif self.short_ema[0] < self.long_ema[0] and self.short_ema[-1] >= self.long_ema[-1]:
            self.sell()

class MACDStrategy(bt.Strategy):
    params = (
        ("fast_period", 12),    # Fast EMA period for MACD
        ("slow_period", 26),    # Slow EMA period for MACD
        ("signal_period", 9),   # Signal line period
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close,
                                       period_me1=self.params.fast_period,
                                       period_me2=self.params.slow_period,
                                       period_signal=self.params.signal_period)

    def next(self):
        if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1]:
            self.buy()
        elif self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1]:
            self.sell()

class BollingerBreakoutStrategy(bt.Strategy):
    params = (
        ("bb_period", 20),       # Period for Bollinger Bands
        ("bb_dev", 2),           # Standard deviation for Bollinger Bands
    )

    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(self.data.close,
                                                       period=self.params.bb_period,
                                                       devfactor=self.params.bb_dev)
        
    def next(self):
        if self.data.close[0] > self.bollinger.lines.bot[0]:
            self.buy()
        elif self.data.close[0] < self.bollinger.lines.top[0]:
            self.sell()

# RSI Strategy
class RSIStrategy(bt.Strategy):
    params = (
        ("rsi_period", 14),     # Period for RSI
        ("rsi_overbought", 70), # Overbought threshold
        ("rsi_oversold", 30),   # Oversold threshold
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)

    def next(self):
        if self.rsi[0] > self.params.rsi_overbought and self.rsi[-1] <= self.params.rsi_overbought:
            self.sell()
        elif self.rsi[0] < self.params.rsi_oversold and self.rsi[-1] >= self.params.rsi_oversold:
            self.buy()

# Parabolic SAR Strategy
class ParabolicSARStrategy(bt.Strategy):
    def __init__(self):
        self.parsar = bt.indicators.ParabolicSAR()

    def next(self):
        if self.data.close[0] > self.parsar[0]:
            self.buy()
        elif self.data.close[0] < self.parsar[0]:
            self.sell()

# ADX and Directional Movement Strategy
class ADXStrategy(bt.Strategy):
    params = (
        ("adx_threshold", 25),   # ADX threshold for trend strength
    )

    def __init__(self):
        self.adx = bt.indicators.AverageDirectionalMovementIndex(period=14)
        self.plus_di = bt.indicators.PlusDI(period=14)
        self.minus_di = bt.indicators.MinusDI(period=14)

    def next(self):
        if self.adx[0] > self.params.adx_threshold and self.plus_di[0] > self.minus_di[0]:
            self.buy()
        else:
            self.sell()

# Ichimoku Cloud Strategy
class IchimokuStrategy(bt.Strategy):
    def __init__(self):
        self.ichimoku = bt.indicators.Ichimoku()

    def next(self):
        if self.data.close[0] > self.ichimoku.lines.senkou_span_a[0] and \
           self.data.close[0] > self.ichimoku.lines.senkou_span_b[0] and \
           self.data.close[-1] <= self.ichimoku.lines.senkou_span_a[-1] and \
           self.data.close[-1] <= self.ichimoku.lines.senkou_span_b[-1]:
            self.buy()
        elif self.data.close[0] < self.ichimoku.lines.senkou_span_a[0] or \
             self.data.close[0] < self.ichimoku.lines.senkou_span_b[0]:
            self.sell()


# Triple Moving Average Crossover
class TripleMAStrategy(bt.Strategy):
    params = (
        ("short_period", 10),   # Short-term MA period
        ("medium_period", 20),  # Medium-term MA period
        ("long_period", 50),    # Long-term MA period
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.medium_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.medium_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if self.short_ma[0] > self.medium_ma[0] > self.long_ma[0] and \
           self.short_ma[-1] <= self.medium_ma[-1] <= self.long_ma[-1]:
            self.buy()
        elif self.short_ma[0] < self.medium_ma[0] < self.long_ma[0] and \
             self.short_ma[-1] >= self.medium_ma[-1] >= self.long_ma[-1]:
            self.sell()

# Moving Average Ribbon Strategy
class MovingAverageRibbonStrategy(bt.Strategy):
    params = (
        ("short_period", 10),   # Short-term MA period
        ("medium_period", 20),  # Medium-term MA period
        ("long_period", 50),    # Long-term MA period
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.medium_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.medium_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if self.short_ma[0] > self.medium_ma[0] > self.long_ma[0]:
            self.buy()
        elif self.short_ma[0] < self.medium_ma[0] < self.long_ma[0]:
            self.sell()


if __name__ == "__main__":
    cerebro = bt.Cerebro()

    # data = bt.feeds.GenericCSVData(
    #     dataname="C:\\Users\\kenne\\Pictures\\All\\python\\forex\\Forex-Trading-Algo2\\Backtest\\DAT_XLSX_EURUSD_M1_2020.csv",  # Replace with the actual file path
    #     fromdate=datetime.datetime(2020, 1, 1),
    #     todate=datetime.datetime(2021, 1, 1),
    #     dtformat=('%Y-%m-%d %H:%M'),
    #     datetime=0,
    #     openinterest=-1
    # )

    data = bt.feeds.GenericCSVData(
        dataname="DAT_XLSX_USDJPY_M1_2020.csv",  # Replace with the actual file path
        fromdate=datetime.datetime(2020, 1, 1),
        todate=datetime.datetime(2020, 8, 5),
        dtformat=('%Y-%m-%d %H:%M'),
        datetime=0,
        openinterest=-1
    )

    cerebro.adddata(data)
    cerebro.addstrategy(MovingAverageRibbonStrategy)

    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.run()
    cerebro.plot()



# note down ADX Strategy
# note down ichimoku strategy
# note down moving average ribbon strategy