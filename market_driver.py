import psycopg as db
import random
import os
from dotenv import load_dotenv, find_dotenv
import transaction_driver
import return_system

# MarketDriver is much more like an API to abstract the transaction driver, I just didn't think about it that way until recently.
class MarketDriver():
	def __init__(self, market_username, market_password, market_host, market_port, market_database, transaction_username, transaction_password, transaction_host, transaction_port, transaction_database):

		self.conn = db.connect(f"postgresql://{market_username}:{market_password}@{market_host}:{market_port}/{market_database}")
		self.cur = self.conn.cursor()

		self.transaction = transaction_driver.TransactionDriver(transaction_username, transaction_password, transaction_host, transaction_port, transaction_database)

	def __del__(self):
		self.conn.close()

	# post function is going to create something on the market
	def post(self, seller_id, account, item_format, item, amount):
		# check account existence, frozen status, and lockdown status
		account_usability = self.transaction.check_usage(seller_id, account)
		if not account_usability:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "Account does is locked down, frozen, or nonexistent according to our systems. Issues? contact devs.")

		# ADD INVENTORY CHECK FOR ITEM
		self.cur.execute("SELECT IDEN FROM Account WHERE IDEN=(%s) AND accountname=(%s)", (str(seller_id), str(account)))
		users = self.cur.fetchall()

		if len(users) <= 0:
			return return_system.returnSystem(False, return_system.NONEXISTENT, "our systems say this account does not exist, if this account actually DOES exist, contact developers")

		# checks if the itemID is a duplicate
		self.cur.execute("SELECT itemID FROM Market;")
		items = self.cur.fetchall()
		[items[0] for items in self.cur.fetchall()]
		itemID = random.randint(10000000, 99999999) # 10 million to 99.999999 million
		while itemID in items:
			itemID = random.randint(10000000, 99999999)

		# inserts into market
		self.cur.execute("INSERT INTO Market (item_format, item, itemid, isforsale, creation_stamp, most_recent_transfer) VALUES (%s, %s, %s, true, Now(), Now()))", ((str(item_format), str(item), int(itemID), int(amount)))) # amount and owner_history are sql lists and will be appended seperately in a below query

		self.cur.execute("UPDATE Market SET owner_history = owner_history || [[(%s), (%s)]] WHERE itemID=(%s) AND item=(%s)", ((int(seller_id), str(account), int(itemID), str(item))))
		self.cur.execute("UPDATE Market SET amount = amount || [%s]", ((int(amount), )))

		self.conn.commit()

		return return_system.returnSystem(True, return_system.SUCCESS, "success")

	def get_all(self):
		self.cur.execute("SELECT SellerIDEN, itemID, saleFormat, item, amount FROM Market")
		item = self.cur.fetchall()
		return item


	def sell(self, item_id, seller_account, seller_id, amount, item_format, item_name):

		# check if account is frozen, existing, or on lockdown
		seller_account_usability = self.transaction.check_usage(seller_id, seller_account)
		if not seller_account_usability:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "Account does is locked down, frozen, or nonexistent according to our systems. Issues? contact devs.")

		# check inventory for item
		self.cur.execute("SELECT inventory FROM Account WHERE accountname=(%s) AND IDEN=(%s)", ((str(seller_account), str(seller_id))))
		# -----------------------------------------
		# SECTION WORKING ON
		has_item = False
		inventory_query = list(self.transaction.cur.fetchall()[0])
		if item_name in inventory_query and item_id in inventory_query:
			has_item = True
		# -----------------------------------------
		# SECTION WORKING ON


		# when post to the market
		self.transaction.cur.execute("INSERT INTO Market (selleriden, saleformat, item, amount, itemID, sellerAccount, creation_stamp) VALUES (%s, %s, %s, %s, %s, %s, Now())", (str(seller_id), str(item_format), str(item_name), int(amount), int(item_id), str(seller_account)))


	def buy(self, item_id, buyer_account, buyer_id):

		buyer_account_usability = self.transaction.check_usage(buyer_id, buyer_account)
		if not buyer_account_usability:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "Account does is locked down, frozen, or nonexistent according to our systems. Issues? contact devs.")

		# get information on seller and item
		self.cur.execute("SELECT SellerIDEN, sellerAccount, amount, item, itemid FROM Market WHERE itemID=(%s)", ((int(item_id),)))
		fetched = self.cur.fetchall()

		if len(fetched) <= 0:
			return return_system.returnSystem(False, return_system.MALFORMED, "This message was returned because the length of the market query has a length less than or equal to zero. Malformed input is possible, but alternative issues are also possible. Contact developers if issue not resolved.")

		# check affordability
		seller_id = fetched[0][0]
		seller_account = fetched[0][1]
		item_amount = fetched[0][2]
		item = fetched[0][3]
		itemid = fetched[0][4]

		## REMEMBER TO UNCOMMENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		"""
		if item_amount > self.transaction.getBalance(buyer_id, buyer_account):
			return return_system.returnSystem(False, return_system.BALANCE_ISSUE, "item_amount > balance")
		"""

		# transfer funds
		transfer_return = self.transaction.transfer(buyer_id, buyer_account, seller_id, seller_account, item_amount)
		if not transfer_return["status"]:
			return return_system.returnSystem(False, return_system.UNKNOWN_ORIGIN, "an issue was found when running a transfer. The origin is unknown. Contact developers - market_driver.buy()")

		# update inventory with new item
		# -------------------------------
		# working on
		self.cur.execute("UPDATE Market SET owner_history = owner_history || [[(%s), (%s)]] WHERE itemID=(%s) AND item=(%s)", ((str(buyer_id), str(buyer_account), int(itemid), str(item))))

		self.cur.execute("UPDATE Market SET isForSale = false WHERE itemID=(%s) AND item=(%s)", ((int(itemid), str(item))))
		self.conn.commit()
		# working on
		# -------------------------------

		return return_system.returnSystem(False, return_system.SUCCESS, "YOUR ITEM HAS BEEN ASSIGNED AN ID {itemID}. YOU CAN USE THE ID TO DELETE THE ITEM. YOU CANNOT ALTER YOUR ITEM")
