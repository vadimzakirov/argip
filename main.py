# -*- coding: utf-8 -*-

import json
import urllib, requests, time, random, hashlib
import urllib2
from cookielib import CookieJar

agripConfig = {"access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc1M0YyNjU3QUZCMDQyMTlDOEU0MzIxN0FGMjA3OUFGNDNCNzZGRUUiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJkVDhtVjYtd1Fobkk1RElYcnlCNXIwTzNiLTQifQ.eyJuYmYiOjE1NTQ3NDQ5MDksImV4cCI6MTU1NDc0ODUwOSwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eXNlcnZlci5hcmdpcC5jb20ucGwiLCJhdWQiOlsiaHR0cHM6Ly9pZGVudGl0eXNlcnZlci5hcmdpcC5jb20ucGwvcmVzb3VyY2VzIiwiYXJnaXBhcGkiXSwiY2xpZW50X2lkIjoiSG1pajVWWXZKd3NwM1ZWdHB6VkRFZTVJVGNNTDlNRHgiLCJzY29wZSI6WyJhcmdpcGFwaSJdfQ.Gxv0h-Uxvo_M2lIVtYn7-1R7rHoLrJFPjSGJydyKaVQtsSfMqn7Ot7B6iL2_h2FgbcXa_s4x6b10FoJSuj_Obee_dL2YbJooe5f-_G5eF28aA2WnVnw3MLS0h2rhryxtiTYF6qELS4SJx6kfkcnZysYoTxdttffjnPTri9UKS244meOPal6vo8b1hvnajXJvwEUfab8rPagNmDT3P1wQA20xsogexz2feHbp_fbpG15637ATGMJC6pRRx0xHyC5_-02oIglfpvjyvL3qRfX7c107W6K7oqvRcJEdIyPatH3EuWNbqqlp3RXV9yR80kWz1dSN2OCSN0D3_xDQI91fYw"}

config = {'access_token': 'ad213ea1de8cdab7e54f2aad44824962'}
mainURL = 'https://struverus.webasyst.cloud/'
lastQuery = time.time();
checkPeriod = 60*60*6 # Checker timeout for Item
def getCur():
	if (db['cur']['updated'] < time.time()):
		try:
			res = urllib.urlopen("https://api.exchangeratesapi.io/latest").read()
			res = json.loads(res)
			db['cur']['val'] = res['rates']['RUB']
			db['cur']['updated'] = time.time() + 60*60*24
		except:
			print 'error with updating currency, try later, using older for 1 hour'
			db['cur']['updated'] = time.time() + 60*60*1
		writeDb(db)
	return db['cur']['val']

def calcPrice(price, priceType):
	#cur = getCur()
	# Calc formula = Price * Currency Price
	#resPrice = float(price) * cur 
	# Saving with rounding
	#resPrice = round(resPrice, 2)
	res = price
	if priceType == 'm':
		res = res * 1.8 * 1.5
	else:
		res = res * 1.8
	return res

def loadDb(dbName = 'qdb.json'):
	f = open(dbName, 'r')
	db = json.loads(f.readline())
	f.close()
	return db

def writeDb(data, dbName = 'qdb.json'):
	toWrite = json.dumps(data)
	f = open(dbName,"w")
	f.write(toWrite)
	f.close()

# config = loadConfig()
def checkToken():
	if db['config']['auth']['expires'] < time.time():
		print 'error, token lost', time.time(), 'seconds... \nloading new token'
		data = "client_id=$CID$&client_secret=$SECRET$&grant_type=client_credentials".replace("$CID$", db['config']['id']).replace("$SECRET$", db['config']['secret'])
		res = urllib.urlopen("https://identityserver.argip.com.pl/connect/token", data).read()
		res = json.loads(res)

		db['config']['auth']['access_token'] = res['access_token']
		db['config']['auth']['expires'] = time.time() + res['expires_in']
		writeDb(db)
	# curl -X POST https://identityserver.argip.com.pl/connect/token -d "client_id=PUT_YOUR_CLIENT_ID&client_secret=PUT_YOUR_CLIENT_SECRET&grant_type=client_credentials"
def apiG(method):
	checkToken()
	token = db['config']['auth']['access_token']
	url = "https://argipapi.argip.com.pl/v1/" + method 
	print url
	# data = urllib.urlencode(jsonParams)
	opener = urllib2.build_opener()
	opener.addheaders.append(('Authorization', "Bearer " + token))
	response = opener.open(url)			

	return json.loads(response.read())

def getItems(page, limit):
	res = apiG("Products/" + str(page) + "/"+str(limit)+"/false")
	return res
def getItem(id):
	res = apiG("Products/" + str(id))
	return res
def getCategoryById(id):
	res = apiG("Categories/" + str(id))
	return res	
def getCategories():
	res = apiG("Categories")
	return res

db = loadDb()
lastQuery = time.time();

# print getCategoryById(0)
# print getItems(0,10)
# print getItem(79)

def api(method, params, jsonParams = {}, token = config['access_token']):
	global lastQuery
	print len(method), 'sending'
	if time.time() - lastQuery < 0.25:
		print 'sleep 0.25'
		time.sleep(0.25)
	lastQuery = time.time();
	#sleep = random.randint(0,2)
	#if sleep:
	#	print 'sleep', sleep
	#	time.sleep(sleep)
	url = mainURL + "api.php/" + method + "?access_token=" + token + '&' + params
	if time.time() - lastQuery < 1:
		time.sleep(1)
		lastQuery = time.time();
	data = urllib.urlencode(jsonParams)
	if (jsonParams != {}):
		req = urllib2.Request(url, data)
	else:
		req = urllib2.Request(url)

	response = urllib2.urlopen(req)
	return json.loads(response.read())
	
def addCategory(name, parent): 
	print 'adding category'
	params = {'name':name};
	if (parent != 0):
		params['parent_id'] = str(parent)
	res = api('shop.category.add', '', jsonParams = params)
	return res
def createSelf(remoteId, name, remoteParent, l = 0):
	if l == 2:
		return 
	try:
		l = db['cats'][str(remoteParent)]
	except:
		print 'passed'
		re = getCategoryById(remoteParent)['PathElements']
		for i in re[::-1]:
			createSelf(i['CategoryId'], i['Name'], i['ParentCategoryId'], l = l + 1)
		exit()
		print 'parrent', remoteId, remoteParent, 'not found'
		return 
	try:
		return db['cats'][str(remoteId)]
	except:
		db['cats'][str(remoteId)] = addCategory(name, createSelf(remoteParent, '', -1))['id']
		print 'saved new category', str(remoteId)
		writeDb(db)
		return createSelf(remoteId, name, remoteParent)
def upgradeCategories():
	print 'start upgrading categories'
	res = getCategories()
	for i in res:
		try:
			createSelf(i['CategoryId'], i['Name'].encode('utf-8'), i['ParentCategoryId'])
		except:
			createSelf(i['CategoryId'], 'unnamed category', i['ParentCategoryId'])

def exist(barCode):
	res = api('shop.product.search', 'hash=search/query=' + str(barCode))
	return res['products']


def getCategory(categoryList, l = 0):
    	if (len(categoryList) == 0 or l > 3):
		return db['cats'][str(-1)]
	else:
		try:
			return db['cats'][str(categoryList[0])]
		except:
			upgradeCategories()
			return getCategory(categoryList, l = l + 1)
def downloadFile(url):
	pass
	return
	urllib.urlretrieve(url, 'test.png')  

def SendFile(pid, token= config['access_token']):
	url = mainURL + "api.php/" + 'shop.product.images.add' + "?access_token=" + token  + "&product_id=" + str(pid)
	# print url
	files = {'file': open('test.png')}
	response = requests.post(url, files=files)

def createElement(item):
	av = 0
	if (item['IsActive']):
		av = 1
	params = {
		# 'skus':'',
		'name': item['ProductFullName'].encode('utf-8').replace("&quot;", " "),
		'price': str(calcPrice(item['YourMainPrice'], "m")),
		'categories[]':getCategory(item['CategoryMapping']),
		"summary": "Размер одной партии " + str(item['SinglePackQuantityInPieces']) + " ед.",
		#'categories':category,
		'sku_type':0,
		'skus[0][name]': 'EanBarcode',
		'skus[0][sku]': item['EanBarcode'],
		'skus[0][virtual]':0,
		'skus[0][price]': str(calcPrice(item['YourMainPrice'], "m")),
		'skus[0][available]': av,
		'skus[0][count]':  int(item['PiecesInStock']),
		"skus[0][purchase_price]": str(calcPrice(item['YourMainPrice'], 's'))

		# 'skus':[{'virtual':1, 'sku':art}],
	}
	res = api('shop.product.add', '', jsonParams = params)['id']
	print res, 'uploaded',
	try:
		print 'try to download and send photo'
		downloadFile(item['PictureUrl'])
		SendFile(res)
	except:
		try:
			print 'URL:', item['PictureUrl']
			downloadFile(item['PictureUrl'])
			SendFile(res)
		except:
			pass
		print 'error with uploading photo not found'
def checkItem(item):
	try:
		if db['checked'][str(item['EanBarcode'])] > time.time():
			return 
	except:
		pass
	print item['EanBarcode'], 'started',
	res = exist(item['EanBarcode'])
	if len(res) == 0:
		createElement(item)
	else:
		res = res[0]
		print "=",res['id']
		update = 0
		sku = api("shop.product.skus.getInfo", "id=" + str(res['sku_id']))
		if float(str(sku['price'])) != float(str(calcPrice(item['YourMainPrice'], 'm'))):
			print sku['price'], calcPrice(item['YourMainPrice'], 'm')
			update = 1

		if int(sku['available']) != item['IsActive']:
			print 'status update'
			update = 1
		try:
			if sku['count'] == None:
				update = 1
				print 'count update from None to', int(item['PiecesInStock'])
			elif int(sku['count']) != int(item['PiecesInStock']):
				update = 1
				print 'count update from', int(sku['count']), 'to', int(item['PiecesInStock'])
		except:
			print 'error with sku check', sku
			print item
			update = 1 

		if update:
			av = 0
			if item['IsActive']:
				av = 1
			print 'updating'
			
			params = {"id":res['sku_id'], "count": int(item['PiecesInStock']), "product_id": res['id'], "purchase_price": str(calcPrice(item['YourMainPrice'], 's')), "price": str(calcPrice(item['YourMainPrice'], 'm')), "available": av}
			api("shop.product.skus.update", "id=" + str(res['sku_id']), jsonParams = params)
			print 'skus update success'
			#api("shop.product.update", "id=" + str(res['id']), jsonParams = {"summary": "Размер одной партии " + str(item['SinglePackQuantityInPieces']) + " ед."})
			#print 'product description update success'
		print 'force update SIZE'
		api("shop.product.update", "id=" + str(res['id']), jsonParams = {"summary": "Размер одной партии " + str(item['SinglePackQuantityInPieces']) + " ед."})
	db['checked'][str(item['EanBarcode'])] = time.time() + checkPeriod
	writeDb(db)
	# print res

def main():
	upgradeCategories()
	mx = 1000000
	l = 0
	totalList = []
	for i in range(50):
		res = getItems(i, 1000)
		if (res == []):
			break
		totalList += res
	print 'starting checking', len(totalList)
	for item in totalList[::-1]:
		print l, 'from', len(totalList),
		l+=1
		try:
			checkItem(item)
	        except:
			print 'error with', item
#main()
#checkItem({u'Index': u'FBG-12030-7  o1', u'YourMainPrice': 26.28, u'BoxWeight': 2.66, u'MultiPackEanBarcode': u'5907601198981', u'NearestDilivery': u'-', u'OtherPossibleQuantity': 0, u'TaxRate': 23.0, u'ProductFullName': u'Screw connectors for profiles  8.8 zinc plated AN 605', u'YourPriceLevel2': 0.0, u'YourEanBarcode': u'', u'SinglePackQuantityInPieces': 100, u'PiecesInStock': 9700, u'YourProductFullName': u'', u'Tags': [], u'YourIndex': u'', u'CurrencyId': 2, u'BaseProductId': 63436, u'YourPriceLevel1': 0.0, u'EanBarcode': u'5907601198820', u'CategoryMapping': [], u'ProductId': 126330, u'QuantityLimitLevel1': 0, u'MultiPackQuantityInPieces': 10, u'QuantityLimitLevel2': 0, u'CustomTags': [], u'PictureUrl': u'http://content.argip.com.pl/b322411d-e869-408b-bb2e-2e957cd5e92d.jpg', u'CurrencyName': u'EUR', u'IsActive': True})
#exit()
for i in xrange(100*100):
	try:
		main()
	except:
		print 'error'
	time.sleep(60)
exit()
