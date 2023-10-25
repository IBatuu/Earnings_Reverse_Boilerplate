import pandas as pd
from binance.spot import Spot 
from datetime import datetime
import time, itertools, random, requests, os, data, pymysql
import plotly.graph_objects as chart
import seaborn as sns
from operator import itemgetter
import numpy as np
import plotly.graph_objects as chart
import plotly.graph_objs as chart
from plotly.subplots import make_subplots


# MySQL Configuration
DB_HOST = f'{data.mysql_host}'
DB_USER = f'{data.mysql_username}'
DB_PASSWORD = f'{data.mysql_pass}'  # Replace with your actual MySQL password
DB_NAME = 'NKE_OHLCV' #REPLACE
TABLE_NAME = 'daily_ohlc' #REPLACE

# Set the params for the backtest result folders
current_dir = "Earnings_Reversal"
root_dir = f"C:\\Users\\Backtesting_Tutorial\\{current_dir}"
subDir = "MA-4h-V1"
pct = "pct1"

# Function for the Buy orders
def buy(priceToBuy, date=None, reduceOnly=False, Id=None, size=None, tpsldate=None, tpOrSl=None, tpsl_price=None, tpmult=None, slmult=None):
    global purchasePrice, finalPortfolio, cashAvaliable
    randomNumber = random.randint(0,1000000)
    if reduceOnly == False:
        purchasePrice = priceToBuy
        addPosition(side="Long", price=priceToBuy, date=date, Id=randomNumber, size=size, tpsldate=tpsldate, tpmult=tpmult, slmult=slmult, tpsl_price=tpsl_price)
    else:
        for positionperp in positionsPerpetual:
            if positionperp["Id"] == Id:
                positionperp["tpSlDate"] = tpsldate
                positionperp["tpOrSl"] = tpOrSl
                positionperp["tpsl_price"] = tpsl_price
# Function for the Sell orders
def sell(priceToSell, date=None, reduceOnly=False, Id=None, size=None, tpsldate=None, tpOrSl=None, tpsl_price=None, tpmult=None, slmult=None):
    global salePrice, finalPortfolio, cashAvaliable
    randomNumber = random.randint(0,1000000)
    if reduceOnly == False:
        salePrice = priceToSell
        addPosition(side="Short", price=priceToSell, date=date, Id=randomNumber, size=size, tpsldate=tpsldate, tpmult=tpmult, slmult=slmult, tpsl_price=tpsl_price)
    else:
        for positionperp in positionsPerpetual:
            if positionperp["Id"] == Id:
                positionperp["tpSlDate"] = tpsldate
                positionperp["tpOrSl"] = tpOrSl   
                positionperp["tpsl_price"] = tpsl_price
# Function that's being called whenever there is a Buy or Sell order to add position unless it's a SL or TP order
def addPosition(side, price, date, Id, size, tpsldate, tpOrSl=None, tpsl_price=None, tpmult=None, slmult=None):
    if side == "Long":
        positionsPerpetual.append({"Side": side, "Size": size, "Price": price, "Date": date, "Id": Id, "PriceToTakeProfit": round(price * tpmult), "PriceToStopLoss": round(price * slmult), "tpSlDate": tpsldate, "tpOrSl": tpOrSl, "tpsl_price": tpsl_price})
    if side == "Short":
        positionsPerpetual.append({"Side": side, "Size": size, "Price": price, "Date": date, "Id": Id, "PriceToTakeProfit": round(price * tpmult), "PriceToStopLoss": round(price * slmult), "tpSlDate": tpsldate, "tpOrSl": tpOrSl, "tpsl_price": tpsl_price})

# Calculate the MAs of your choice
def calculate_moving_average(data):
    window_size = 7  # change this to adjust the moving average window size
    moving_averages = []
    for i in range(window_size - 1):
        moving_averages.append(None)

    for i in range(window_size - 1, len(data)):
        window_sum = sum([d['Close'] for d in data[i - window_size + 1:i + 1]])
        moving_average = window_sum / window_size
        moving_averages.append(moving_average)

    for i, d in enumerate(data):
        d['Moving Average'] = moving_averages[i - window_size + window_size]

    return data
def calculate_moving_average200(data):
    window_size = 100  # change this to adjust the moving average window size
    moving_averages = []
    for i in range(window_size - 1):
        moving_averages.append(None)

    for i in range(window_size - 1, len(data)):
        window_sum = sum([d['Close'] for d in data[i - window_size + 1:i + 1]])
        moving_average = window_sum / window_size
        moving_averages.append(moving_average)

    for i, d in enumerate(data):
        d['Moving Average200'] = moving_averages[i - window_size + window_size]

    return data
def calculate_moving_average300(data):
    window_size = 300  # change this to adjust the moving average window size
    moving_averages = []
    for i in range(window_size - 1):
        moving_averages.append(None)

    for i in range(window_size - 1, len(data)):
        window_sum = sum([d['Close'] for d in data[i - window_size + 1:i + 1]])
        moving_average = window_sum / window_size
        moving_averages.append(moving_average)

    for i, d in enumerate(data):
        d['Moving Average300'] = moving_averages[i - window_size + window_size]

    return data

# Function for fetching data from DB takes three parameters two of which are necessary
def fetch_data_from_db(mode, date1, date2=None):
    # Connect to MySQL
    connection = pymysql.connect(host=DB_HOST,
                                user=DB_USER,
                                password=DB_PASSWORD,
                                db=DB_NAME)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    # Formulate query based on mode
    if mode == "specific":
        query = f"SELECT * FROM {TABLE_NAME} WHERE date = %s"
        cursor.execute(query, (date1,))
    elif mode == "range":
        query = f"SELECT * FROM {TABLE_NAME} WHERE date BETWEEN %s AND %s"
        cursor.execute(query, (date1, date2))
    elif mode == "after":
        query = f"SELECT * FROM {TABLE_NAME} WHERE date > %s"
        cursor.execute(query, (date1,))
    elif mode == "before":
        query = f"SELECT * FROM {TABLE_NAME} WHERE date < %s"
        cursor.execute(query, (date1,))
    
    results = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return results

# These are timestamps for the beginning of some years. Usage of them is optional and can be used while gathering data if for example one wants to gather data that's later than X year
year = 1502798400000 # 1514764800000, 1546300800000, 1577836800000, 1609459200000,1640995200000

earnings_dates_for_nke = [datetime.utcfromtimestamp(ts) for ts in [
            1380229200, 1387486800, 1395349200, 1403816400, 1411678800, 1418936400, 1426798800, 1435266000, 1443128400, 1450299600, 1458680400, 1467147600, 1475010000, 1482267600, 1490130000, 1498770000, 1506459600, 1513890000, 1521752400, 1530219600, 1537909200, 1545339600, 1553202000, 1561669200, 1569358800, 1576789200, 1585083600, 1593118800, 1600808400, 1608325200,
            1616101200, 1624568400, 1632430800, 1640034000, 
            1647896400, 1656363600, 1664485200, 1671570000, 
            1679432400, 1688072400]]

yearEndingCash = []
startTime = year
blankTime = year 
directoryYear = datetime.fromtimestamp(startTime/1000.0).strftime('%y')
try:
    parent_dir = f"{root_dir}"
    directory = f"{subDir}"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
except Exception as e:
    print(e)
    pass
try:
    parent_dir = f"{root_dir}\\{directory}"
    directory = f"Y{directoryYear}"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
except Exception as e:
    print(e)
    pass
try:
    parent_dir = f"{root_dir}\\{subDir}\\{directory}"
    directory = f"{pct}"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
except Exception as e:
    print(e)
    pass


earnings_day_counter = 0
closing_price_next_day_of_earnings = None
price_change_30d_after_earnings = None
def backtest():
    global positions, close, positionsPerpetual, pct, directoryYear, subDir, startTime, blankTime, earnings_day_counter, price_change_30d_after_earnings, closing_price_next_day_of_earnings
    dirTime = startTime 
    tp = 0
    sl = 0
    close = []
    positions = []
    positionsPerpetual = []
    directoryDate = datetime.fromtimestamp(dirTime/1000.0).strftime('%d-%m-%y')
    directory = f"{directoryDate}"
    # Parent Directory path
    parent_dir = f"{root_dir}\\{subDir}\\Y{directoryYear}\\{pct}"
    # Path
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    portfolioColumns = ["Date", "Starting Balance", "Profits Taken", "Stops Taken", "Ending Balance"]
    portfolioDf = pd.DataFrame(columns=portfolioColumns)

    tradesColumns = ['Side', 'Size', 'Price', 'Date', 'Id', "TpSl Price", "TP or SL"]
    tradesDf = pd.DataFrame(columns=tradesColumns)
    timestamp = []
    high = []
    low = []
    open = []
    close = []
    volume = []
    ma = []
    ma2 = []
    ma3 = []
    dataDict = []
    ma300Touched = True
    openPosition = 0
    tradeIv = "85"

    ################################################################################################
    start_date = "2017-01-01" #yyy/mm/dd
    end_date = "2023-10-10" #yyy/mm/dd
    data = fetch_data_from_db("range", start_date, end_date)
    ################################################################################################

    for entry in data:
        date_str = entry['date'].strftime('%Y-%m-%d %H.%M.%S')
        timestamp.append(date_str)
        open.append(entry['open'])
        high.append(entry['high'])
        low.append(entry['low'])
        close.append(entry['close'])
        volume.append(entry['volume'])
        
        dictionary = {
            "Date": date_str,
            "Open": entry['open'],
            "High": entry['high'],
            "Low": entry['low'],
            "Close": entry['close'],
            "Volume": entry['volume'],
            "Pump Score": 0,
            "Dump Score": 0,
            "Significance": None,
            "Index": None,
            "Traded": False
        }
        dataDict.append(dictionary)

    dataDict = calculate_moving_average(dataDict)
    dataDict = calculate_moving_average200(dataDict)
    dataDict = calculate_moving_average300(dataDict)
    for avg in dataDict:
        ma.append(avg["Moving Average"])
        ma2.append(avg["Moving Average200"])
        ma3.append(avg["Moving Average300"])

    cash_values = []
    cash_timestamps = []

    figure1 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.01,
        subplot_titles=("Nike inc -- NKE", "Cash Value"))
    figure1.add_trace(chart.Candlestick(x=timestamp, open=open, high=high, low=low, close=close), row=1, col=1)
    figure1.add_trace(chart.Scatter(x=timestamp, y=ma, line=dict(color='red', width=1)), row=1, col=1)
    figure1.add_trace(chart.Scatter(x=timestamp, y=ma2, line=dict(color='lightgrey', width=1)), row=1, col=1)
    figure1.add_trace(chart.Scatter(x=timestamp, y=ma3, line=dict(color='white', width=1)), row=1, col=1)

    
    figure1.update_layout(
        title="Nike inc -- NKE",
        yaxis_title="Price",
        plot_bgcolor="black",
        paper_bgcolor="black",
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            tickmode="auto",
            nticks=30,
            gridcolor="rgba(0, 0, 0, 0)",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        yaxis=dict(
            gridcolor="rgba(0, 0, 0, 0)",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        xaxis2=dict(
            tickmode="auto",
            nticks=30,
            gridcolor="rgba(0, 0, 0, 0)",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        yaxis2=dict(
            gridcolor="rgba(0, 0, 0, 0)",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),
        title_font=dict(color="white"),
        legend=dict(font=dict(color="white")),
        margin=dict(t=50, b=50, l=50, r=50)
    )


    score = 0
    priceIndex = 0
    countMe = 0
    for point in dataDict:
        point["Index"] = priceIndex

        if earnings_day_counter == 1:
            closing_price_next_day_of_earnings = point["Close"]

        if earnings_day_counter != 0:
            earnings_day_counter += 1
        
        
        priceIndex += 1
        size = round((333333 * 1)/point["Close"])
        current_day_in_backktest = datetime.strptime(point["Date"], '%Y-%m-%d %H.%M.%S')
        current_ts_in_ms = current_day_in_backktest.timestamp() * 1000
        #################################### SET CONDITIONS TO LONG OR SHORT ####################################
        
        for earning_date in earnings_dates_for_nke:
            if (earning_date.year == current_day_in_backktest.year and
                earning_date.month == current_day_in_backktest.month and
                earning_date.day == current_day_in_backktest.day):
                if earnings_day_counter == 0:
                    earnings_day_counter += 1
        if earnings_day_counter == 30 and price_change_30d_after_earnings == None:
            if closing_price_next_day_of_earnings < point["Close"]:
                price_change_30d_after_earnings = "Positive"
                print(closing_price_next_day_of_earnings, point["Close"], "Positive")

            else:
                price_change_30d_after_earnings = "Negative"
                print(closing_price_next_day_of_earnings, point["Close"], "Negative")

        if 33 > earnings_day_counter >= 30:
            if price_change_30d_after_earnings == "Positive":
                sell(priceToSell=point["Close"], date=current_ts_in_ms, size=size, tpmult=0.1, slmult=10)
            else:
                buy(priceToBuy=point["Close"], date=current_ts_in_ms, size=size, tpmult=10, slmult=0.1)
            
        #if 63 > earnings_day_counter >= 60:
        #    if positionsPerpetual != []:
        #        for position in positionsPerpetual:
        #            if position["Side"] == "Long":
        #                sell(priceToSell=point["Close"], date=current_ts_in_ms, size=size, tpsl_price=point["Close"], tpmult=0.1, slmult=10)
        #                break
        #            if position["Side"] == "Short":
        #                buy(priceToBuy=point["Close"], date=current_ts_in_ms, size=size, tpsl_price=point["Close"], tpmult=10, slmult=0.1)
        #                break
        
        if earnings_day_counter == 56:
            earnings_day_counter = 0
            price_change_30d_after_earnings = None
            closing_price_next_day_of_earnings = None
        
        if positionsPerpetual != []:
            for position in positionsPerpetual:
                if position["Side"] == "Long":
                    if position["tpOrSl"] == None:
                        if point["Open"] > point["Close"]:
                            if (position["PriceToTakeProfit"] <= point["High"]) and (current_ts_in_ms > position["Date"]):                    
                                sell(priceToSell=position["PriceToTakeProfit"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=position["PriceToTakeProfit"])
                            elif (position["PriceToStopLoss"] >= point["Low"]) and (current_ts_in_ms >= position["Date"]):
                                sell(priceToSell=position["PriceToStopLoss"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=position["PriceToStopLoss"])
                            else:
                                if 56 > earnings_day_counter >= 53 and position["Price"] > point["Close"] and (current_ts_in_ms > position["Date"]):
                                    sell(priceToSell=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=point["Close"])
                                    break
                                elif 56 > earnings_day_counter >= 53 and position["Price"] < point["Close"] and (current_ts_in_ms > position["Date"]):
                                    sell(priceToSell=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=point["Close"])
                                    break
                        else:
                            if (position["PriceToStopLoss"] >= point["Low"]) and (current_ts_in_ms > position["Date"]):
                                sell(priceToSell=position["PriceToStopLoss"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=position["PriceToStopLoss"])
                            elif (position["PriceToTakeProfit"] <= point["High"]) and (current_ts_in_ms >= position["Date"]):       
                                    sell(priceToSell=position["PriceToTakeProfit"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=position["PriceToTakeProfit"])
                            else:
                                if 56 > earnings_day_counter >= 53 and position["Price"] > point["Close"] and (current_ts_in_ms > position["Date"]):
                                    sell(priceToSell=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=point["Close"])
                                    break
                                elif 56 > earnings_day_counter >= 53 and position["Price"] < point["Close"] and (current_ts_in_ms > position["Date"]):
                                    sell(priceToSell=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=point["Close"])
                                    break
                if position["Side"] == "Short":
                    if position["tpOrSl"] == None:
                        if point["Open"] < point["Close"]:
                            if (position["PriceToTakeProfit"] >= point["Low"]) and (current_ts_in_ms > position["Date"]):
                                buy(priceToBuy=position["PriceToTakeProfit"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=position["PriceToTakeProfit"])
                            elif (position["PriceToStopLoss"] <= point["High"]) and (current_ts_in_ms >= position["Date"]):
                                buy(priceToBuy=position["PriceToStopLoss"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=position["PriceToStopLoss"])
                            else:
                                if 56 > earnings_day_counter >= 53 and position["Price"] < point["Close"] and (current_ts_in_ms > position["Date"]):
                                    buy(priceToBuy=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=point["Close"])
                                    break
                                elif 56 > earnings_day_counter >= 53 and position["Price"] > point["Close"] and (current_ts_in_ms > position["Date"]):
                                    buy(priceToBuy=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=point["Close"])
                                    break
                        else:
                            if (position["PriceToStopLoss"] <= point["High"]) and (current_ts_in_ms > position["Date"]):
                                buy(priceToBuy=position["PriceToStopLoss"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=position["PriceToStopLoss"])
                            elif (position["PriceToTakeProfit"] >= point["Low"]) and (current_ts_in_ms >= position["Date"]):
                                buy(priceToBuy=position["PriceToTakeProfit"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=position["PriceToTakeProfit"])
                            else:
                                if 56 > earnings_day_counter >= 53 and position["Price"] < point["Close"] and (current_ts_in_ms > position["Date"]):
                                    buy(priceToBuy=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="sl", tpsl_price=point["Close"])
                                    break
                                elif 56 > earnings_day_counter >= 53 and position["Price"] > point["Close"] and (current_ts_in_ms > position["Date"]):
                                    buy(priceToBuy=point["Close"], Id=position["Id"], reduceOnly=True, size=position["Size"], tpsldate=current_ts_in_ms, tpOrSl="tp", tpsl_price=point["Close"])
                                    break
    perpIndex = 0
    openPositions = 0
    positionsPerpetualSorted = sorted(positionsPerpetual, key=lambda d: (d['Date'], -d['Price'] if d['Side'] == 'Long' else d['Price']))
    for num in range(len(positionsPerpetualSorted)):
        for i in range(len(positionsPerpetualSorted)):
            if positionsPerpetualSorted[i]["Date"] <= blankTime:
                del positionsPerpetualSorted[i]
                break
            
    # IF ONE POSITION AT A TIME IS WANTED, UNCOMMENT BELOW
    #for perp in positionsPerpetualSorted: 
    #    for closedP in positionsPerpetualSorted[perpIndex:]:
    #        try:
    #            if perp["tpSlDate"] >= closedP["Date"]:
    #                openPositions += 1
    #                if openPositions > 1:
    #                    positionsPerpetualSorted.remove(closedP)
    #            else:
    #                openPositions = 0
    #                break
    #        except Exception as e:
    #            print(e)
    #            positionsPerpetualSorted.remove(closedP)
    #            pass
    #    perpIndex += 1
    cash = 1000000
    portfolioDf.at[0, "Starting Balance"] = cash 
    for perp in positionsPerpetualSorted:
        if perp["Side"] == "Short":
            cash = cash + (perp["Size"] * perp["Price"])
            cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
            cash_values.append(cash)
            figure1.add_trace(chart.Scatter(
                x=[str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                y=[perp["Price"]],
                mode="markers+text",
                marker=dict(symbol='star-triangle-down-open', size= 25, color= 'red')))
            if perp["tpOrSl"] == "sl":
                sl += 1
                cash = cash - (perp["Size"] * perp["tpsl_price"])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
                figure1.add_trace(chart.Scatter(
                    x=[str(datetime.fromtimestamp(int(perp["tpSlDate"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                    y=[perp["tpsl_price"]],
                    mode="markers+text",
                    marker=dict(symbol='x', size= 25, color= 'red')))
            if perp["tpOrSl"] == "tp":
                tp += 1
                cash = cash - (perp["Size"] * perp["tpsl_price"])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
                figure1.add_trace(chart.Scatter(
                    x=[str(datetime.fromtimestamp(int(perp["tpSlDate"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                    y=[perp["tpsl_price"]],
                    mode="markers+text",
                    marker=dict(symbol='cross', size= 25, color= 'green')))
            if perp["tpOrSl"] == None:
                cash = cash - (perp["Size"] * close[-1])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
        if perp["Side"] == "Long":
            cash = cash - (perp["Size"] * perp["Price"])
            cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
            cash_values.append(cash)
            figure1.add_trace(chart.Scatter(
                x=[str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                y=[perp["Price"]],
                mode="markers+text",
                marker=dict(symbol='star-triangle-up-open', size= 25, color= 'green')))
            if perp["tpOrSl"] == "sl":
                sl += 1
                cash = cash + (perp["Size"] * perp["tpsl_price"])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
                figure1.add_trace(chart.Scatter(
                    x=[str(datetime.fromtimestamp(int(perp["tpSlDate"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                    y=[perp["tpsl_price"]],
                    mode="markers+text",
                    marker=dict(symbol='x', size= 25, color= 'red')))
            if perp["tpOrSl"] == "tp":
                tp += 1
                cash = cash + (perp["Size"] * perp["tpsl_price"])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
                figure1.add_trace(chart.Scatter(
                    x=[str(datetime.fromtimestamp(int(perp["tpSlDate"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S'))],
                    y=[perp["tpsl_price"]],
                    mode="markers+text",
                    marker=dict(symbol='cross', size= 25, color= 'green')))
            if perp["tpOrSl"] == None:
                cash = cash + (perp["Size"] * close[-1])
                cash_timestamps.append(str(datetime.fromtimestamp(int(perp["Date"])/1000, tz=None).strftime('%Y-%m-%d %H.%M.%S')))
                cash_values.append(cash)
        tradesDf.loc[len(tradesDf.index)] = [perp["Side"], perp["Size"], perp['Price'] , perp['Date'], perp['Id'], perp['tpsl_price'], perp['tpOrSl']]
    print(cash)
    # Add the cash value trace
    figure1.add_trace(chart.Scatter(x=cash_timestamps, y=cash_values, line=dict(color='orange', width=1)), row=2, col=1)
    figure1.update_yaxes(showgrid=False, row=2, col=1)  # Removes horizontal grid lines for the subplot at row 2, col 1
    figure1.update_xaxes(showgrid=False, row=2, col=1)  # Removes vertical grid lines for the subplot at row 2, col 1

    portfolioDf.at[0, "Ending Balance"] = cash 
    portfolioDf.at[0, "Profits Taken"] = tp 
    portfolioDf.at[0, "Stops Taken"] = sl
    portfolioFile = 'Portfolio.csv'
    tradesFile = 'Trades.csv'
    figureFile = f'Candlestick{year}.html'
    portfolioDf.to_csv(rf"{parent_dir}\{directory}\{portfolioFile}", index=False)
    tradesDf.to_csv(rf"{parent_dir}\{directory}\{tradesFile}", index=False)
    figure1.write_html(rf"{parent_dir}\{directory}\{figureFile}")
    yearEndingCash.append(cash-1000000)
    print("Year Ending Profits:", sum(yearEndingCash))

backtest()

print(earnings_dates_for_nke)
