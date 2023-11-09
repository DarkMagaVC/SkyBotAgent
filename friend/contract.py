'''THIS FILE HAS CODE TO INTRACT WITH THE CONTRACT'''
import web3
from eth_account import Account


class Contract:
    def __init__(self, contractAddress="0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4", BASE_MAINNET="https://developer-access-mainnet.base.org/", privateKey=None):
        self.CONTRACT_ADDRESS = contractAddress
        self.PRIVATE_KEY = privateKey
        self.BASE_MAINNET = BASE_MAINNET

    def getBuyPrice(self, address, amount):
            '''returns buy price of shares in wei'''

            checkSumAddress = web3.Web3.to_checksum_address(address)
            w3 = web3.Web3(web3.HTTPProvider(self.BASE_MAINNET))
            contractABI = open("./friend/contractABI.json", "r").read()
            contract = w3.eth.contract(
                address=self.CONTRACT_ADDRESS, abi=contractABI)
            buyPrice = contract.functions.getBuyPrice(
                w3.to_checksum_address(checkSumAddress), amount).call()
            return buyPrice
