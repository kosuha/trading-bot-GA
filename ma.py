from random import randrange
import pyupbit
import pandas as pd
import numpy as np
import random

pd.set_option('display.float_format', lambda x: '%.5f' % x)

# 데이터 분석을 위한 테이터 가져오기
# day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month
def get_data(coin, test_data_interval, test_length, test_end_date):
	date = test_end_date
	length = test_length + 240
	df = pyupbit.get_ohlcv(coin, interval=test_data_interval, to=date, count=length)
	df.to_excel("./data/btc.xlsx")
	print(df)

def backtest(small, large, profit, loss):
	df = pd.read_excel("./data/btc.xlsx")
	df['mas'] = df['close'].rolling(window=small).mean().shift(1)
	df['mal'] = df['close'].rolling(window=large).mean().shift(1)
	df = df[239:]
	df['long'] = np.where((df['mas'] > df['mal']) & (df['mas'].shift(1) <= df['mal'].shift(1)), 1, 0)
	# print(df)
	price_list = list(df['close'])
	listlen = len(price_list)
	i = 239
	position = 0
	buy_price = 0
	hpr = 1.0
	while i < listlen:
		if position == 0 and df.at[i, 'long'] == 1:
			position = 1
			buy_price = df.at[i, 'close']
		elif position == 1:
			if df.at[i, 'close'] >= buy_price * profit:
				position = 0
				hpr *= (df.at[i, 'close'] / buy_price) - 0.0015
			if df.at[i, 'close'] <= buy_price * (1 - loss):
				position = 0
				hpr *= (df.at[i, 'close'] / buy_price) - 0.0015
		i += 1
	if position == 1:
		hpr *= (df.at[i - 1, 'close'] / buy_price) - 0.0015
	return [small, large, profit, loss, hpr]

def evolution(survivor_list, gen_profit, gen_loss):
	if len(survivor_list) > 50:
		survivor_list = survivor_list[-50:]
	small_list = []
	large_list = []
	profit_list = []
	loss_list = []
	for i in range(0, len(survivor_list)):
		small_list.append(survivor_list[i][0])
		large_list.append(survivor_list[i][1])
		profit_list.append(survivor_list[i][2])
		loss_list.append(survivor_list[i][3])
	for i in range(0, len(survivor_list) // 10):
		small_list.append(random.randint(1, 240))
		large_list.append(random.randint(1, 240))
		profit_list.append(random.choice(gen_profit))
		loss_list.append(random.choice(gen_loss))
	return small_list, large_list, profit_list, loss_list

def generation(small_list, large_list, profit_list, loss_list):
	gene_list = []
	for i in range(0, 200):
		gene_list.append([random.choice(small_list), random.choice(large_list), random.choice(profit_list), random.choice(loss_list)])
	survivor_list = []
	for i in range(0, 200):
		temp = backtest(gene_list[i][0], gene_list[i][1], gene_list[i][2], gene_list[i][3])
		# if temp[-1] >= 1.0:
		survivor_list.append(temp)
	survivor_list.sort(key=lambda x:x[-1])
	# print(survivor_list)
	return survivor_list

def main():
	# get_data("KRW-BTC", "minute1", 60 * 24 * 7, "20220921 00:00:00")
	# res = backtest(-139, 86)
	# print(res)
	gen_profit = []
	gen_loss = []
	for i in range(1, 20):
		gen_profit.append(i * 0.005)
		gen_loss.append(i * 0.005)

	survivor_list = generation(range(1, 240), range(1, 240), gen_profit, gen_loss)
	gen_count = 10
	i = 0
	while i < gen_count:
		if len(survivor_list) < 5:
			print("멸종")
			break
		print(f"{i}	generation")
		print(f"생존:	{len(survivor_list)}")
		print(f"TOP5:	{survivor_list[-5:]}\n")
		small_list, large_list, profit_list, loss_list = evolution(survivor_list, gen_profit, gen_loss)
		survivor_list = generation(small_list, large_list, profit_list, loss_list)
		i += 1

if __name__ == "__main__":
    main()