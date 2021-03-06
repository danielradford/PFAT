import numpy as np
from zipline.api import(    symbol,
                            order_target_percent,
                            schedule_function,
                            date_rules,
                            time_rules,
                            record
                       )

def initialize(context):
    schedule_function(check_pairs,date_rules.every_day(),time_rules.market_close(minutes=60))

    context.universe=[symbol('AAL'),symbol('UAL')]
   

    context.long_on_spread = False
    context.shorting_spread = False

def check_pairs(context,data):

    aa = context.universe[0]
    ual = context.universe[1]

    prices = data.history([aa,ual],'price',30,'1d')

    short_prices = prices.iloc[-1:]

    # all using the spread 
    mavg_30 = np.mean(prices[aa]-prices[ual])
    std_30 = np.std(prices[aa]-prices[ual])
    mavg_1 = np.mean(short_prices[aa] - short_prices[ual])

    if std_30 > 0: 
        zscore = (mavg_1 - mavg_30 ) / std_30

        if zscore > 1.0 and not context.shorting_spread:
            order_target_percent(aa,-0.5)
            order_target_percent(ual,0.5)
            context.shorting_spread = True
            context.long_on_spread = False

        elif zscore < 1.0 and not context.long_on_spread:
            order_target_percent(aa,0.5)
            order_target_percent(ual,-0.5)
            context.shorting_spread = False
            context.long_on_spread = True

        elif abs(zscore) < 0.1:
            order_target_percent(aa,0)
            order_target_percent(ual,0)
            context.shorting_spread = False
            context.long_on_spread = False

        record(Z_score = zscore)
