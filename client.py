import discord
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
import transaction_driver
import os

load_dotenv(find_dotenv())

username = os.getenv("USER")
password = os.getenv("PSWD")
database = os.getenv("DBNM")
key = os.getenv("KEY")

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
base_driver = transaction_driver.TransactionDriver(username, password, "localhost", 5432, database)

@client.event
async def on_ready():
	print("logged in as {0.user}".format(client))
	synced = await client.tree.sync()
	print(synced)


#@discord.app_commands.describe(member="send to")
@client.tree.command(name="transfer", description="transfer funds")
@discord.app_commands.describe(transfer_amount="transfer amount")
@discord.app_commands.describe(sender_account="account transfer out")
async def transfer(interaction: discord.Interaction, member: discord.Member, recipient_account: str, sender_account: str, transfer_amount: int):
	sender_account = sender_account
	sender_id = interaction.user.id
	recipient_id = member.id
	recipient_account = recipient_account
	transfer_amount = transfer_amount
	output = base_driver.transfer(sender_id, sender_account, recipient_id, recipient_account, transfer_amount)
	if output["status"] == True:
		await interaction.response.send_message("transaction carried out!", ephemeral=True)
	else:
		await interaction.response.send_message('f{output["message"]}')


# latency/version ping
@client.tree.command(name="ping", description="ping xchangr")
async def ping(interaction: discord.Interaction):
	await interaction.response.send_message(f"`` | xchangr | 0.1.0 unstable beta | LAT {client.latency} | ``")


# account creation
@client.tree.command(name="create", description="account_name")
@discord.app_commands.describe(account_name="enter account name")
@discord.app_commands.choices(account_type=[
	discord.app_commands.Choice(name="Individual Personal Account", value="individual"),
	discord.app_commands.Choice(name="Corporate Account", value="corporate"),
])
async def create(interaction: discord.Interaction, account_name: str, account_type: discord.app_commands.Choice[str]):
	isCompany = False
	if account_type == "corporate":
		isCompany = True
	output = base_driver.create_account(account_name, interaction.user.id, isCompany, False)
	await interaction.response.send_message(f'{output["message"]}', ephemeral=True)

# get balanace for specific account
@client.tree.command(name="balance", description="get balance for specific account")
@discord.app_commands.describe(account_name="account name")
async def get_account_balance(interaction: discord.Interaction, account_name: str):
	await interaction.response.send_message(f'{base_driver.getBalance(account_name, interaction.user.id)}', ephemeral=True)

# if __name__ == "__main__":
while True:
	client.run(key)
