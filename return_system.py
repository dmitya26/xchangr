INVALID_AMOUNT = "ERROR: Invalid Transaction Amount"
FRAUD_DETECTED = "ERROR: Fraudulent Transaction Detected"
INCOMPLETE     = "ERROR: Incomplete Feature"
FORBIDDEN      = "ERROR: This action is forbidden"
NONEXISTENT    = "ERROR: Account does not exist"
MALFORMED      = "ERROR: Malformed Input"
UNKNOWN_ORIGIN = "ERROR: UNKNOWN ORIGIN"
BALANCE_ISSUE  = "ERROR: Invalid Balance"
SUCCESS        = "SUCCESS"

def returnSystem(status, message, hint):
	message = f"{message} ({hint})"
	temporary = {
		"status":status,
		"message":message
	}
	return temporary
