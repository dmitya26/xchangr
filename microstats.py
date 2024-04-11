
"""
micro-scale statistics:
        credit score
		credit rating
        bond rating
"""

import numpy as np

class CreditScore():
	# -9 - 10
	def payment_history(self, weeks_since_account_creation, percentage_of_loans_fully_paid, percentage_of_payments_on_time):
		weeks_since_account_creation    = float(weeks_since_account_creation)
		percentage_of_loans_fully_paid 	= float(percentage_of_loans_fully_paid)
		percentage_of_payments_on_time  = float(percentage_of_payments_on_time)

		if weeks_since_account_creation <= 9:
			weeks_since_account_creation = weeks_since_account_creation * -1

		sigmoid = 100*(1/(1+np.exp(weeks_since_account_creation*-1)))

		sigmoid = 100 if sigmoid > 99.9 else sigmoid # make sure to test this if statement variable, I haven't tested it yet...

		all_params = [sigmoid, percentage_of_loans_fully_paid, percentage_of_payments_on_time]
		mean = sum(all_params)/len(all_params)
		return mean

	def amounts_owed(self, debts_list, earnings_list):
		all_debts = sum(debts_list)
		debt_mean = all_debts/len(debts_list)

		all_earnings = sum(earnings_list)
		earnings_mean = all_earnings/len(earnings_list)

		mad = sum([abs(debts_list[i] - debt_mean) for i in range(len(debts_list))]) / len(debts_list)
		debt_ratio = all_debts/all_earnings

		#return [all_debts, debt_mean, mad, debt_metric]
		THE_DEBT_FACTOR = 100-(debt_ratio*2)
		return THE_DEBT_FACTOR

	def credit_mix(self, loan_history):
		loan_types = ["credit_card", "home_equity", "ARM", "FRM", "secured", "unsecured"]
		filtered_loan_history = [loan_history[i][0] for i in range(len(loan_history)) if loan_history[i][2] in loan_types and not loan_history[i][1]]

		percent_home_equity_deviation = 100*(filtered_loan_history.count("home_equity")/len(filtered_loan_history))-100/6
		percent_credit_card_deviation = 100*(filtered_loan_history.count("credit_card")/len(filtered_loan_history))-100/6
		percent_ARM_deviation = 100*(filtered_loan_history.count("ARM")/len(filtered_loan_history))-100/6
		percent_FRM_deviation = 100*(filtered_loan_history.count("FRM")/len(filtered_loan_history))-100/6
		percent_secured_deviation   = 100*(filtered_loan_history.count("secured"))-100/6
		percent_unsecured_deviation = 100*(filtered_loan_history.count("unsecured"))-100/6

		deviation_list = [percent_home_equity_deviation, percent_credit_card_deviation, percent_ARM_deviation, percent_FRM_deviation, percent_secured_deviation, percent_unsecured_deviation]
		deviation_list.remove(max(deviation_list))
		deviation_list.remove(min(deviation_list))

		mean_deviation = sum(deviation_list)/len(deviation_list)
		mix_measurement = 100-(mean_deviation*2)
		return mix_measurement


	# loan_history = [[amount, is_default_boolean_type, "loan_type"], [amount, is_default_boolean_type, "loan_type"]]
	def creditScore(self, weeks_since_account_creation, percentage_of_loans_fully_paid, percentage_of_payments_on_time, debts_list, earnings_list, loan_history): # debts list is just a list of total debt payments in numbers

		history = self.payment_history(weeks_since_account_creation, percentage_of_loans_fully_paid, percentage_of_payments_on_time)
		amounts = self.amounts_owed(debts_list, earnings_list)
		factors = [history, amounts]
		score = sum(factors)/len(factors) # credit score

		defaulted_score = 0

		loan_history = np.array(loan_history)
		if np.shape(loan_history)[1] > 0:
			for i in range(len(loan_history)):
				# 12% credit score demerit for every default
				if loan_history[1]:
					#print("FFFF")
					defaulted_score += ((score/1)*(12/100))
					#print(defaulted_score)

		score = score-defaulted_score
		return int(10*(score))
