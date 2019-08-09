import os
import csv
import jwt    
import time
import uuid
import shutil
import requests
from datetime import datetime
import hashlib
import time
from urllib.parse import urlencode
from ast import literal_eval

def Auth_Token():
	payload = {
	    'access_key': [ACCESS_KEY],
	    'nonce': str(uuid.uuid4()),
	}

	jwt_token = jwt.encode(payload, [SECRET_KEY]).decode('utf-8')
	authorization_token = 'Bearer {}'.format(jwt_token)  

	return authorization_token


def my_wallet():
	params = {'Authorization': Auth_Token()}
	url="https://api.upbit.com/v1/accounts"
	result = requests.get(url, headers=params)
	wallet_list = result.json()

	url = "https://api.upbit.com/v1/candles/minutes/1"
	show_btc = {"market":"KRW-BTC", "count":"1"}
	btc_result = requests.get(url, params=show_btc)
	btc_price = btc_result.json()[0]['trade_price']
	
	global krw
	krw=0
	global btc
	btc=0
	global btc2

	for i in range(0,len(wallet_list)):
		
		wallet_list[i] = str(wallet_list[i]).replace("'",'"')
		wallet_dic = literal_eval(wallet_list[i])
		
		if wallet_dic['currency'] == 'KRW':
			krw = wallet_dic['balance']
			
		elif wallet_dic['currency'] == 'BTC':
			btc = float(wallet_dic['balance'])
			btc2 = float(wallet_dic['balance'])*btc_price

	print("원화 : "+krw + "원")	
	print("비트코인 : " +str(btc2) + "원")

	krw = float(krw)

	global ok
	if int(krw) < int(btc2):
		ok=1
	else:
		ok=0


def cross(sh,lo):
	print(ok)

	if sh>=lo:

		if ok == 0:
			buy_btc()
		else:
			pass

	else:

		if ok == 1:
			sell_btc()
		else:
			pass


def buy_btc():
	print("btc 구매")
	query = {
	    'market': 'KRW-BTC',
	    'side': 'bid',
	    'price': krw-5000,
	    'ord_type': 'price',
	}
	query_string = urlencode(query).encode()

	m = hashlib.sha512()
	m.update(query_string)
	query_hash = m.hexdigest()

	payload = {
	    'access_key': [ACCESS_KEY],
	    'nonce': str(uuid.uuid4()),
	    'query_hash': query_hash,
	    'query_hash_alg': 'SHA512',
	    "executed_volume":"0.0"
	}

	jwt_token = jwt.encode(payload, [SECRET_KEY]).decode('utf-8')
	authorize_token = 'Bearer {}'.format(jwt_token)
	headers = {"Authorization": authorize_token}

	res = requests.post('https://api.upbit.com' + "/v1/orders", params=query, headers=headers)

	print(res)
	print(res.text)
	print(res.json()['created_at'])


def sell_btc():
	print("btc 판매")
	query = {
	    'market': 'KRW-BTC',
	    'side': 'ask',
	    'volume':  btc-0.00035,
	    'ord_type': 'market',
	}
	query_string = urlencode(query).encode()

	m = hashlib.sha512()
	m.update(query_string)
	query_hash = m.hexdigest()

	payload = {
	    'access_key': [ACCESS_KEY],
	    'nonce': str(uuid.uuid4()),
	    'query_hash': query_hash,
	    'query_hash_alg': 'SHA512',
	    "executed_volume":"0.0"
	}

	jwt_token = jwt.encode(payload, [SECRET_KEY]).decode('utf-8')
	authorize_token = 'Bearer {}'.format(jwt_token)
	headers = {"Authorization": authorize_token}

	res = requests.post('https://api.upbit.com' + "/v1/orders", params=query, headers=headers)

	print(res)
	print(res.text)
	print(res.json()['created_at'])


def Moving_Average_Line(response):
	modify = response.text
	modify = modify.replace("[","")
	modify = modify.replace("]","")
	form = modify.split(",{")
	price_sum = 0
	
	first_value = literal_eval(form[0])
	print("기간 합계, 기간 평균")
	price_sum = first_value['trade_price']
	for i in range(1,len(form)):
		value = "{"+form[i]
		value = literal_eval(value)
		price_sum += value['trade_price']

	price_average = (price_sum / len(form))

	print(price_sum, price_average)

	return price_average


def Candle30_Line15():
	url = "https://api.upbit.com/v1/candles/minutes/10"
	short_line = {"market":"KRW-BTC", "count":"3"}
	long_line = {"market":"KRW-BTC", "count":"6"}

	s_response = requests.get(url, params=short_line)
	l_response = requests.get(url, params=long_line)

	sh=Moving_Average_Line(s_response)
	lo=Moving_Average_Line(l_response)

	save_data[3]=str(sh)
	save_data[4]=str(lo)
	
	cross(sh,lo)	
	
if __name__=="__main__":
	desktop_path=os.getenv('USERPROFILE')+"\\Desktop"
	save_data=[]
	save_data.append(['시간','원화', '비트코인', '30분봉 5이동평균선 평균', '30분봉 20이동평균선 평균', '비트코인 보유현황(보유=1)', '가 치'])
	file = open(desktop_path+'\\original.csv', 'a', encoding='euc_kr', newline='')
	csvfile = csv.writer(file)

	for row in save_data:
	    csvfile.writerow(row)
	file.close()
	save_data=[0,0,0,0, 0,0,0]

	while(1):
		my_wallet()
		Candle30_Line15()
		my_wallet()


		save_data[0]=datetime.now()
		save_data[1]=str(krw)
		save_data[2]=str(btc2)
		save_data[5]=str(ok)
		save_data[6]=str(krw+btc2)

		for i in save_data:
			print(i)
		file = open(desktop_path+'\\original2.csv', 'a', encoding='euc_kr', newline='')
		csvfile = csv.writer(file)

		csvfile.writerow(save_data)
		file.close()
		try:
			shutil.copy(desktop_path+'\\original.csv', desktop_path+'\\copy.csv')
		except PermissionError as a:
			shutil.copy(desktop_path+'\\original.csv', desktop_path+'\\copy2.csv')
		time.sleep(60)