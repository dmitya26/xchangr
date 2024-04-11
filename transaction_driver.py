import psycopg as db
import dotenv
import os
import re
import return_system
from dotenv import load_dotenv, find_dotenv
import threading
from datetime import datetime # REMEMBER TO USE THIS IMPORT
import asyncio

import bcrypt

# transaction driver is essentailly the backbone of the project, it handles all of the rudimentary database operations, like account creation, account freezing, currency transfers, etc...
class TransactionDriver:
	def __init__(self, username, password, host, port, database):
		self.conn = db.connect(f"postgresql://{username}:{password}@{host}:{port}/{database}")
		self.cur = self.conn.cursor()

	def __del__(self):
		self.conn.close()

	def check_account(self, user_id, account):
		self.cur.execute("SELECT IDEN, accountname, isLockdown, isCompany FROM Account WHERE IDEN=(%s) AND accountname=(%s)",(str(user_id), str(account)) )
		fetchedAccountQueries = self.cur.fetchall()

		if len(fetchedAccountQueries) > 0:
			return True
		return False
		# query = [second_dimension for second_dimension in fetchedAccountQueries[0]]

	def get_all_accounts(self, uid):
		self.cur.execute("SELECT accountname FROM Account WHERE IDEN=(%s)", ((str(uid), )))
		accounts = self.cur.fetchall()
		return [i[0] for i in accounts]


	def _checkFrozen(self, uid, account_name):
		self.cur.execute("SELECT isFrozen FROM Account WHERE accountname=(%s) AND IDEN=(%s)", ((str(account_name), str(uid))))
		getIsFrozen = self.cur.fetchall()[0][0]
		return getIsFrozen

	def _checkLockdown(self, uid, account_name):
		self.cur.execute("SELECT isLockdown FROM Account WHERE accountname=(%s) AND IDEN=(%s)", ((str(account_name), str(uid))))
		getIsLockdown = self.cur.fetchall()[0][0]
		return getIsLockdown

	def check_usage(self, uid, account_name):
		isFrozen = self._checkFrozen(uid, account_name)
		isLockdown = self._checkLockdown(uid, account_name)
		accountExists = self.check_account(uid, account_name)

		if isFrozen or isLockdown or not accountExists:
			return False

		return True

	def generate_funds(self, uid, account, amount):
		self.cur.execute("INSERT INTO Ledger (iden, account, amount, stamp) VALUES (%s, %s, %s, Now())", (int(uid), str(account), int(amount)))
		self.conn.commit()

	# submit record into "Ledger" table
	def transfer(self, sender_id, sender_account_name, recipient_id, recipient_account_name, transferAmount) -> dict:
 		# check account existence, lockdown or frozen
		sender_usable = self.check_usage(sender_id, sender_account_name)
		recipient_usable = self.check_usage(recipient_id, recipient_account_name)
		if not sender_usable or not recipient_usable:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "account is either frozen, locked down, or doesn't exist according to our systems. Issue? consult devs.")

		# execute queries and perform some extra validation on tranfer amount and typing
		if transferAmount > 0 and type(transferAmount*100) == int:
			# sender query
			tmp = (transferAmount * 100)*-1
			self.cur.execute("INSERT INTO Ledger (iden, account, amount, stamp) VALUES (%s, %s, %s, Now())", (sender_id, sender_account_name, tmp))

			# reciever
			tmp = transferAmount * 100
			self.cur.execute("INSERT INTO Ledger (iden, account, amount, stamp) VALUES (%s, %s, %s, Now())", (recipient_id, recipient_account_name, tmp))

		else:
			return return_system.returnSystem(False, return_system.INVALID_AMOUNT, "maybe you entered a Negative Number or a long decimal number (examples: 10.11111111 or -10")

		self.conn.commit()
		return return_system.returnSystem(True, return_system.SUCCESS, "United Channels credit transfer")

	def getBalance(self, account_name, user_id):
		# get all transactions for a specific user_id and account_name
		self.cur.execute("SELECT amount FROM Ledger WHERE account=(%s) AND IDEN=(%s)", ((str(account_name), str(user_id))))
		transactions_tuple = self.cur.fetchall()
		transactions = [transactions[0] for transactions in transactions_tuple]
		return sum(map(int, transactions))
		#return re.findall(r'[+-]?\d+', transactions)
		#return sum(map(int, re.findall(r'[+-]?\d+', transactions)))

	# create account in "Account" table
	def create_account(self, account_name, user_id, isCompany, highProfileFunds):
		self.cur.execute("SELECT accountname FROM Account WHERE IDEN=(%s)", ((str(user_id), )))
		users = self.cur.fetchall()
		users = [i[0] for i in users]
		if account_name in users:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "can account with this name already exists")

		self.cur.execute("INSERT INTO Account (accountname, iden, isfrozen, isCompany, highProfileFunds, isLockdown, creation_stamp) VALUES (%s, %s, %s, %s, %s, %s, Now())", (account_name, user_id, False, isCompany, highProfileFunds, False))
		self.conn.commit()

		# check users==0 because funds are generated and allocated only if it's a first time account
		if len(users) == 0: # checks if accounts are zero still because variable was defined before account was inserted into the database
			self.generate_funds(user_id, account_name, 1000)

		return return_system.returnSystem(True, "created account or company", f"Company accounts have the ability to be linked with what are called 'companies'. Companies are just features which are added to the xchangr bot (and which perform actions automatically). You don't actually do anything for a company, you just configure a few things, and the company will run")

	"""
	def create_company(self, account_name, user_id):
		self.cur.execute("INSERT INTO Account (accountname, iden, isfrozen, isCompany) VALUES (%s, %s, %s, %s)", [[account_name, user_id, False, True]])
	"""

	# REMEMBER TO FINISH THIS FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# DON'T FORGET TO FINISH THIS FUNCTION
	# FEATURE NOT WORKING YET, DON'T FORGET TO FINISH THIS TOMORROW
	# (this is a day later, I legitimately do not remember what I needed to finish, all of this looks good lmao)
	def close_account(self, closing_account_name, transfer_account_name, user_id):
		closing_usable  = self.check_usage(user_id, closing_account_name)
		transfer_usable = self.check_usage(user_id, transfer_account_name)

		self.cur.execute("SELECT accountname FROM Account WHERE IDEN=(%s);", (str(user_id),))
		users = self.cur.fetchall()

		user_exists = False
		user_list = [i[0] for i in users]
		if len(user_list) <= 1:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "there are no accounts to transfer to")

		if not closing_usable or not transfer_usable:
			return return_system.returnSystem(False, return_system.FORBIDDEN, "this account either does not exist, is frozen, or is locked down according to our systems. Issues? consult devs.")


		amount_transfer = self.getBalance(closing_account_name, user_id)
		self.transfer(user_id, closing_account_name, user_id, transfer_account_name, amount_transfer)

		self.cur.execute("DELETE FROM Account WHERE accountname=(%s) AND IDEN=(%s)", ((str(closing_account_name), str(user_id))))
		self.conn.commit()

		return return_system.returnSystem(True, return_system.SUCCESS, f"United Channels account {closing_account_name} CLOSED and funds transfered to {transfer_account_name}")

	# lockdown account(s) from all transactions using password
	def lockdown(self, user_id, scope, password) -> dict: # scope - lock a single account, or lock all of your accounts

		if scope != "all":
			account_usable = self.account_usage(user_id, scope)
			if not account_usable:
				return return_system.returnSystem(False, return_system.FORBIDDEN, "this account is either nonexistent, frozen, or locked down. Issues? contact devs.")

		self.cur.execute("SELECT accountname FROM Account WHERE IDEN=(%s);", (str(user_id),))
		users = self.cur.fetchall()

		user_exists = False
		user_list = [i[0] for i in users]


		hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

		if scope == "all":
			self.cur.executemany("UPDATE Account SET islockdown=true WHERE (IDEN=%s)", [[str(user_id)]])
			self.cur.executemany("UPDATE Account SET lockdownPassword=%s WHERE (IDEN=%s)", [[hashed_password, str(user_id)]])
			self.conn.commit()
			return return_system.returnSystem(True, return_system.SUCCESS, "United Channels Account Lockdown")

		elif len(account) > 0:
			self.cur.executemany("UPDATE Account SET islockdown=true WHERE (accountname=%s AND IDEN=%s)", [[account_name, str(user_id)]])
			self.cur.executemany("UPDATE Account SET lockdownPassword=%s WHERE (accountname=%s AND IDEN=%s)", [[hashed_password, account_name, str(user_id)]])
			self.conn.commit()
			return return_system.returnSystem(True, return_system.SUCCESS, "United Channels Account {scope} Lockdown")

		else:
			return return_system.returnSystem(False, return_system.NONEXISTENT, "try creating an account or checking spelling, if you already have an account, contact developers")

	# unlock a previously locked account
	def unlock(self, user_id, scope, password):
		# some validation checks
		if scope != "all":
			account_usable = self.account_usage(user_id, scope)
			if not account_usable:
				return return_system.returnSystem(False, return_system.FORBIDDEN, "the account is either nonexistent, frozen, or locked down according to our systems. Issues? consult devs.")

		self.cur.execute("SELECT accountname FROM Account WHERE IDEN=(%s)", (str(user_id),))
		accounts_query = self.cur.fetchall()
		accounts = [accounts[0] for accounts in accounts_query]

		if scope not in accounts and scope != "all":
			return return_system.returnSystem(False, return_system.NONEXISTENT, "our systems think this account doesn't exist. If this is wrong, contact the developers.")

		# prepared string generation
		sql_lockdown, sql_password, password_query, string_parameters = "", "", "", ()
		if scope == "all":
			password_query = "SELECT lockdownPassword FROM Account WHERE IDEN=(%s)" # change "SELECT DISTINCT" to "SELECT"
			sql_lockdown = "UPDATE Account SET isLockdown=false WHERE IDEN=(%s)"
			sql_password = "UPDATE Account SET lockdownPassword='' WHERE IDEN=(%s)"
			string_parameters = (str(user_id),)
		else:
			password_query = "SELECT lockdownPassword FROM Account WHERE IDEN=(%s) AND accountname=(%s)" # change "SELECT DISTINCT" to "SELECT"
			sql_lockdown = "UPDATE Account SET isLockdown=false WHERE IDEN=(%s) AND accountname=(%s)"
			sql_password = "UPDATE Account SET lockdownPassword='' WHERE IDEN=(%s) AND accountname=(%s)"
			string_parameters = (str(user_id), str(scope),)

		self.cur.execute(password_query, string_parameters)
		hashed_password = self.cur.fetchall()[0][0]

		# password check and lockdown deactivation
		if bcrypt.checkpw(password.encode(), hashed_password):
			self.cur.execute(sql_lockdown, string_parameters)
			self.conn.commit()

			self.cur.execute(sql_password, string_parameters)
			self.conn.commit()


			return return_system.returnSystem(True, return_system.SUCCESS, f"United Channels Account {scope} Unlocked")
		return return_system.returnSystem(False, return_system.FORBIDDEN, "our systems think you entered your password incorrectly. If you KNOW you entered it correctly, contact developers")

	def freeze(self, uid, account_name):
		self.cur.execute("UPDATE Account SET isFrozen=true WHERE accountname=(%s) AND IDEN=(%s)", ((str(account_name), str(uid))))
		self.conn.commit()

	def unfreeze(self, uid, account_name):
		self.cur.execute("UPDATE Account SET isFrozen=false WHERE accountname=(%s) AND IDEN=(%s)", ((str(account_name), str(uid))))
		self.conn.commit()



