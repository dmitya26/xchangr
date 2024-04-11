import unittest
from dotenv import load_dotenv, find_dotenv
import os
import transaction_driver
import market_driver
import microstats

class TestDrivers(unittest.TestCase):

	# @unittest.skip("testing market driver")
	def test_transaction_driver(self):
		load_dotenv(find_dotenv())
		username = os.getenv("USER")
		password = os.getenv("PASS")
		database = os.getenv("DBNM")

		driver = transaction_driver.TransactionDriver(username, password, "localhost", 5432, database)

		driver.create_account("checking", 123456789, False, False)
		driver.create_account("checking", 123456780, False, False)
		driver.create_account("MonkeyButt Co", 987654321, True, False)
		driver.create_account("savings",  246813579, False, False)
		print("CREATE 3 ACCOUNTS AND ONE COMPANY")

		transfer = driver.transfer(123456789, "checking", 246813579, "savings", 200)
		#check = driver.check_account("checking", 123456789)
		lockdown = driver.lockdown(123456789, "all", "password123")
		unlock = driver.unlock(123456789, "all", "password123")
		# relockdown = driver.lockdown(123456789, "all", "password123")

		abc123 = driver.create_account("abc123", 222333, False, False)
		xyz456 = driver.create_account("xyz456", 222333, False, False)
		print("abc123 ", abc123)
		print("xyz456 ", xyz456)
		close = driver.close_account("abc123", "xyz456", 222333)

		driver.create_account("HELLO", 135790, False, False)
		check = driver.check_account(987654321, "MonkeyButt Co")

		self.assertTrue(transfer["status"], msg="transfer failed")
		print(transfer)

		self.assertTrue(lockdown["status"], msg="lockdown failed")
		print(lockdown)

		self.assertTrue(unlock["status"], msg="unlock failed")
		print(unlock)

		"""
		self.assertTrue(relockdown["status"], msg="relockdown failed")
		print(relockdown)
		"""
		self.assertTrue(close["status"], msg=f"{close['message']}")
		print(close)

		self.assertTrue(check, msg="account check failed")
		print(check)

		driver.freeze(135790, "HELLO")
		driver.unfreeze(135790, "HELLO")


	@unittest.skip("testing market driver")
	def test_market_driver(self):
		load_dotenv(find_dotenv())
		username = os.getenv("USER")
		password = os.getenv("PASS")
		database = os.getenv("DBNM")

		base_driver = transaction_driver.TransactionDriver(username ,password, "localhost", 5432, database)
		mk = market_driver.MarketDriver(username, password, "localhost" ,5432, database, username, password, "localhost" ,5432, database)
		item_post = mk.post(987654321, "MonkeyButt Co", "Bond", "UCTB0139", 18472)
		item_buy  = mk.buy(56967203, "checking", 123456789)
		#item_sell = mk.sell(27952291) # when you sell an item, that item will remain in your inventory until a transaction has been carried out
		item_get  = mk.get_all()

		print(item_post)
		print(item_buy)
		#print(item_sell)
		print(item_get)

	@unittest.skip("testing credit score")
	def test_credit_score(self):
		score = microstats.CreditScore()

		history_test_1 = score.payment_history(100, 100, 100)
		history_test_2 = score.payment_history(0, 0, 0)

		self.assertTrue(history_test_1, 100.0)
		print("history test 1")

		self.assertTrue(history_test_2, 0.0)
		print("history test 2")

		amounts_owed_test = score.amounts_owed([1, 1], [1, 1])
		self.assertTrue(amounts_owed_test, 100)
		print("owed amounts percent score: ", amounts_owed_test)

		creditscore = score.creditScore(100, 100, 100, [0, 0, 0], [1, 1, 1], [[]])
		print("final scocre percent format: ", creditscore)


if __name__ == "__main__":
	unittest.main()
