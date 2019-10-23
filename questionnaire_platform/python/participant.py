from Crypto.Util import number
from Crypto.Random import random
import sys
import util
import json
from web3 import Web3
from solc import compile_files, link_code, compile_source
from web3.contract import ConciseContract

sys.setrecursionlimit(5000)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
owner = w3.eth.accounts[3]

class Participant:
    def __init__(self, g, N, h):
        self.N = N
        self.g = g
        self.h = h
        # self.r = random.randint(1, N/4)

    def decryptQuestion(hex_text):
        ans = ""
        i = 2
        while i < len(hex_text):
            temp = chr(int(hex_text[i:i+2], 16))
            ans += temp
            i = i+2
        return ans

    def decrypteAllQuestions(qs):
        ans = []
        for i in range(len(qs)):
            ans.append(decryptQuestion(qs[i]))
        for i in range(len(ans)):
            print(ans[i])
        return ans

    def showAllQuestions(qs):
        ans = decrypteAllQuestions(qs)
        for i in range(len(ans)):
            print(ans[i])

    def encryption(self, m):
        N2 = self.N*self.N
        r = random.randint(1, self.N//4)
        cm1 = util.calculate_expo_mod (self.g, r, N2)
        cm2_part1 = util.calculate_expo_mod (self.h, r, N2)
        cm2_part2 = (m*self.N%N2)*cm2_part1 % N2
        cm2 = (cm2_part1+cm2_part2) % N2
        # print("cm1: ")
        # print(cm1)
        # print("cm2: ")
        # print(cm2)
        return (cm1, cm2)

    def encryptMultipleChoice(self, list, x): # list represents the answers, x is the number of participants allowed
        length = len(list)*x
        ans = 0
        for i in range(len(list)):
            for j in range(x):
                ans = ans << 1;
            if list[i] > 0:
                ans = ans | list[i]
        print("bit representation of answers: ")
        print(ans)
        print(bin(ans))
        return self.encryption(ans)

def answerQuestionnaire(contract_instance, qs_count):
    print("which questionnaire?")
    for i in range(qs_count):
        # print(str(i+1) + ". " + Web3.toText())
        # print(Web3.toText(contract_instance.getQuestionnaireTitle(i+1, transact={'from':owner})))
        print(contract_instance.getQuestionnaireTitle(i+1, transact={'from':owner}))
    id = int(input())
    # public_key_list = []
    public_key_list = contract_instance.getQuestionnaireKey(id, transact={'from':owner})
    print(public_key_list)
    q_types = contract_instance.getQuestionnaireQTypes(id, transact={'from':owner})
    # public_key_list, q_count, title, content, q_types, par_count
    # for i in range(16):
    #     public_key_list.append(contract_instance.questionnaires[id].publicKey(i))
    public_key = util.mergeToBigInt(public_key_list)
    par = Participant(g, N, public_key)
    print("questionnaire content: ")
    content = contract_instance.getQuestionnaireContent(id, transact={})
    print(content)
    # q_list = par.decrypteAllQuestions(content)
    # q_count = contract_instance.questionnaires[id].questionCount()
    cm1 = []
    cm2 = []
    for i in range(q_count):
        q_type = q_types[i]
        # print(q_list[i])
        print("your choice: ")
        if q_type == 1 or q_type == 4:
            ans = int(input())
            temp1, temp2 = par.encryption(ans)
            temp1_list = util.splitBigInt(temp1)
            temp2_list = util.splitBigInt(temp2)
            cm1.append(temp1_list)
            cm2.append(temp2_list)
        elif q_type == 2 or q_type == 3:
            ans = str(input())
            ans = ans.replace(' ', '')
            ans_list = ans.split(',')
            temp1, temp2 = par.encryptMultipleChoice(ans_list, 8)
            temp1_list = util.splitBigInt(temp1)
            temp2_list = util.splitBigInt(temp2)
            cm1.append(temp1_list)
            cm2.append(temp2_list)
    tx_hash = contract_instance.addParticipant(id, cm1, cm2, transact={'from':owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)


if __name__=="__main__":
    with open("data.json", 'r') as f:
        datastore = json.load(f)
        config = datastore
    contract_instance = w3.eth.contract(address=config['contract_address'], abi=config['abi'], ContractFactoryClass=ConciseContract)
    NList = util.readBigIntFromContract(contract_instance, "N")
    gList = util.readBigIntFromContract(contract_instance, "g")
    N = util.mergeToBigInt(NList)
    g = util.mergeToBigInt(gList)
    while True:
        print("Choose what you want to do: ")
        print("1. answer a questionnaire")
        print("2. quit")
        choice = int(input())
        if choice == 1:
            qs_count = contract_instance.questionnaireCount()
            if qs_count < 1:
                print("No existing questionnaire yet.")
                continue;
            answerQuestionnaire(contract_instance, qs_count)
        elif choice == 2:
            sys.exit(1)
        else:
            print("invalid choice")
