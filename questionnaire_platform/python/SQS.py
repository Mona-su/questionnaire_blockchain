from Crypto.Util import number
from Crypto.Random import random
import sys
import util
import json
from web3 import Web3
from solc import compile_files, link_code, compile_source
from web3.contract import ConciseContract
import os

sys.setrecursionlimit(5000)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
owner = w3.eth.accounts[1]
w3.eth.defaultAccount = w3.eth.accounts[1]

def deploy_contract(N, g, h2):
    # compile all contract files
    # contracts = compile_files(['C:/Users/Mona/Documents/study/Yr3_summer/URFP/project/questionnaire_platform/contractsQuestionnaire.sol',
    #     'C:/Users/Mona/Documents/study/Yr3_summer/URFP/project/questionnaire_platform/SafeMath.sol'])
    # contracts = compile_files(["../contracts/Questionnaire.sol", "../contracts/SafeMath.sol"])
    # # separate main file and link file
    # main_contract = contracts.pop("../contracts/Questionnaire.sol:Questionnaire")
    # library_link = contracts.pop("../contracts/SafeMath.sol:SafeMath")

    # Instantiate and deploy library contract
    with open("../build/contracts/SafeMath.json", 'r') as f:
        datastore = json.load(f)
        library_abi = datastore["abi"]
        library_bytecode = datastore["bytecode"]

    library_contract = w3.eth.contract(
        abi=library_abi,
        bytecode=library_bytecode
    )
    # Get transaction hash from deployed contract
    tx_hash =library_contract.constructor().transact()
    # Get tx receipt to get contract address
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    address = tx_receipt['contractAddress']
    library_address = {
        "../contracts/SafeMath.sol:SafeMath": address
    }

    with open("../build/contracts/Questionnaire.json", 'r') as f:
        datastore = json.load(f)
        main_abi = datastore["abi"]
        main_bytecode = datastore["bytecode"]

    # main_bytecode = link_code(main_abi, library_address)

    # Instantiate and deploy main (Questionnaire) contract
    main_contract_inst = w3.eth.contract(
        abi=main_abi,
        bytecode=main_bytecode
    )
    tx_hash = main_contract_inst.constructor(N, g, h2).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    address = tx_receipt['contractAddress']
    contract_address = address

    config = {
        "abi": main_abi,
        "address": contract_address
    }
    with open('data.json', 'w') as outfile:
        data = {
            "abi": main_abi,
            "contract_address": contract_address
        }
        json.dump(data, outfile, indent=4, sort_keys=True)
    return config


class SQS:
    def __init__(self, N, g):
        self.N = N
        self.g = g

    def generateSQSKeys(self):
        N2 = self.N*self.N
        self.__b = random.randint(1, N2//4)
        # self.__b = random.randint(1, 15)
        self.h2 = util.calculate_expo_mod (self.g, self.__b, N2) # is p and q 1024 bits, will have problem here
        # print("h2: ")
        # print(self.h2)

    def getSQSPublicKey(self):
        return self.h2

    def decryptNumberFirst (self, cm1, cm2):
        N2 = self.N*self.N
        # temp = (cm1**self.__b)%N2
        temp = util.findMI(util.calculate_expo_mod(cm1, self.__b, N2), N2)
        # return (cm1, cm2/temp)
        return (cm1, cm2*temp%N2)

    def decryptMatrixFirst (self, matrix1, matrix2):
        for i in range(len(matrix1)):
            for j in range(len(matrix1)):
                if i < j:
                    matrix1[i][j], matrix2[i][j] = self.decryptNumberFirst(matrix1[i][j], matrix2[i][j])
        return matrix1, matrix2


if __name__=="__main__":
    g, N = util.generateKeys(512)
    gList = util.splitBigInt(g)
    NList = util.splitBigInt(N)
    sqs = SQS(N, g)
    sqs.generateSQSKeys()
    h2 = sqs.getSQSPublicKey()
    h2List = util.splitBigInt(h2)
    config = deploy_contract(NList, gList, h2List)
    contract_instance = w3.eth.contract(address=config['address'], abi=config['abi'], ContractFactoryClass=ConciseContract)
    data = contract_instance.questionnaireCount()
    print(data)
