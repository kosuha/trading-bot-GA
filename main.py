from random import randrange
import pyupbit
import pandas as pd
import numpy as np
import random

pd.set_option('display.float_format', lambda x: '%.2f' % x)

# 데이터 분석을 위한 테이터 가져오기
# day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month
def get_data(coin, test_data_interval, test_length, test_end_date):
	date = test_end_date
	length = test_length
	df = pyupbit.get_ohlcv(coin, interval=test_data_interval, to=date, count=length)
	df['middle'] = df['close'].rolling(window=20).mean()
	std = df['close'].rolling(20).std(ddof=0)
	df['upper'] = df['middle'] + 2 * std
	df['lower'] = df['middle'] - 2 * std
	df = df[19:]
	df['deviation'] = (df['close'] - df['middle']) / (df['upper'] - df['middle']) * 100
	df.to_excel("./data/btc.xlsx")

def backtest(lc, sc):
	df = pd.read_excel("./data/btc.xlsx")
	df['long'] = np.where(df['deviation'] < lc, 1, 0)
	df['short'] = np.where(df['deviation'] > sc, 1, 0)
	long_list = list(df['long'])
	short_list = list(df['short'])
	listlen = len(long_list)
	i = 0
	position = 0
	buy_price = 0
	hpr = 1.0
	while i < listlen:
		if position == 0 and long_list[i] == 1:
			position = 1
			buy_price = df.at[i, 'close']
		elif position == 1 and short_list[i] == 1:
			position = 0
			hpr *= (df.at[i, 'close'] / buy_price) - 0.0015
		i += 1
	return [lc, sc, round(hpr, 3)]

def evolution(survivor_list):
	if len(survivor_list) > 50:
		survivor_list = survivor_list[-50:]
	lc_list = []
	sc_list = []
	for i in range(0, len(survivor_list)):
		lc_list.append(survivor_list[i][0])
		sc_list.append(survivor_list[i][1])
	for i in range(0, len(survivor_list) // 10):
		lc_list.append(random.randint(-150, 150))
		sc_list.append(random.randint(-150, 150))
	return lc_list, sc_list

def generation(lc_list, sc_list):
	gene_list = []
	for i in range(0, 100):
		gene_list.append([random.choice(lc_list), random.choice(sc_list)])
	survivor_list = []
	for i in range(0, 100):
		temp = backtest(gene_list[i][0], gene_list[i][1])
		if temp[2] > 1.0:
			survivor_list.append(temp)
	survivor_list.sort(key=lambda x:x[2])
	return survivor_list

def main():
	get_data("KRW-BTC", "minute60", 24 * 14, "20220921")
	# res = backtest(106, 140)
	# print(res)
	survivor_list = generation(range(-150, 150), range(-150, 150))
	gen_count = 10
	i = 0
	while i < gen_count:
		if len(survivor_list) > 5:
			print("멸종")
			break
		print(f"{i}	generation")
		print(f"생존:	{len(survivor_list)}")
		print(f"TOP5:	{survivor_list[-5:]}\n")
		lc_list, sc_list = evolution(survivor_list)
		survivor_list = generation(lc_list, sc_list)
		i += 1

if __name__ == "__main__":
    main()