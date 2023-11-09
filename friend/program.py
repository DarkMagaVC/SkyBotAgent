import friendtech
import time
import psycopg2
import web3
import random
from friend.contract import Contract
from datetime import datetime

class Program:
    def __init__(self, twitter=None, USER_ADDRESS="0x8abCd876d0398285F9C2B2f9fE1d0Ef40e1af0B1", CONTRACT_ADDRESS="0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4", BASE_MAINNET="https://developer-access-mainnet.base.org/", privateKey=None):
        self.USER_ADDRESS = USER_ADDRESS
        self.CONTRACT_ADDRESS = CONTRACT_ADDRESS
        self.BASE_MAINNET = BASE_MAINNET
        self.twitter = twitter
        self.w3 = web3.Web3(web3.HTTPProvider(BASE_MAINNET))

    def my_trades(self):
        interval = 10
        blocks_to_check = 10

        checkSumAddress = web3.Web3.to_checksum_address(self.USER_ADDRESS)
        contractABI = open("./friend/contractABI.json", "r").read()
        contract = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS, abi=contractABI)

        while True:
            latest_block = self.w3.eth.block_number
            past_events = contract.events.Trade().get_logs(fromBlock=latest_block - 10)
            for event in past_events:
                self.handle_event(event)
            time.sleep(interval)


    def handle_event(self, event):
        if event.args.isBuy and event.args.subject == self.USER_ADDRESS:
            print(f"Subject: {event.args.subject}, isBuy: {event.args.isBuy}")
            platform = friendtech.Platform()
            user = platform.getInfoFromAddress(event.args.trader).json()
            self.welcome_new_user(user['twitterUsername'])
        else:
            print("Not a buy event")


    def welcome_new_user(self, user):

        messages = [
            f"🎉 We have a new key holder! ⚡Welcome aboard, @{user}! 🔑 Your journey begins now. 🤖🔷 ",
            f"⭐ New key unlocked! Welcome to our space, @{user}! Your adventure is just getting started. 🚀🔑",
            f"🎯 Bullseye! @{user} is our latest key holder! Time to embark on a thrilling journey. ⌛🔐",
            f"💎 Treasure unlocked! We're thrilled to welcome @{user} aboard. Your quest has officially begun. 🔑⏳",
            f"🔔 Another key claimed! Congrats @{user}, your expedition is underway. 🏹🔑",
            f"✅ Key obtained! Welcome @{user}, get ready for an amazing expedition. 🌍🔐",
            f"🔮 Crystal ball predicts an exciting journey for our new key holder, @{user}! The future is now. ☄️🗝️",
            f"🛸 New explorer alert! @{user}, grab your key. The world is yours to discover. 🌍💫",
            f"⏰ Tick tock, @{user}! Your time as a new key holder starts now. Can't wait to see where the journey takes you. 💼🗝️",
            f"🆕 @{user}, welcome to an extraordinary expedition as our latest key holder! Excited for the adventures ahead. 🏞️🔑",
            f"📍 An extraordinary journey awaits our new key holder @{user}. Buckle up and explore! 📜🔑"
            f"🌅 Welcome, @{user}, to a new dawn of discovery and prosperity. Together, we chart an exciting course. 🧭🔑",
            f"🌈 Good fortune awaits, @{user}! As our new key holder, you're the author of an incredible new chapter. ✍️🔮🔑",
            f"💖 A heartily welcome to you, @{user}! Your key is not just a trinket, it's a ticket to a thrilling voyage. 🎟️🔗🔑",
            f"🕹️ Game on, @{user}! As our latest key holder, you're in for a ride full of wealth and wonders. 🎢💎🔑",
            f"⚜️ Hail @{user}, the newest member in our prestigious key holder club. Your path to glory begins. 👑💰🔑"
        ]

        text = random.choice(messages).format(user=user)
        self.twitter.create_tweet(text=text)
