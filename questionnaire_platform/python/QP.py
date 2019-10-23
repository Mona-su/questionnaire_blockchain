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
owner = w3.eth.accounts[2]
# w3.eth.defaultAccount = w3.eth.accounts[2]

class QP:
    def __init__(self, N, g, h2):
        self.N = N
        self.g = g
        self.h2 = h2

    def generateQPKeys(self):
        N2 = self.N*self.N
        self.__a = random.randint(1, N2//4)
        # self.__a = random.randint(1, 15)
        self.h1 = util.calculate_expo_mod (self.g, self.__a, N2)
        # print("h1: ")
        # print(self.h1)

    def getQPPublicKey(self):
        return self.h1

    def getPublicKey(self):
        N2 = self.N*self.N
        return (self.h1*self.h2)%N2

    def encodeQuestion(text):
        bytes = "0x"
        i = 0
        while i < len(text):
            if text[i] == ':' and text[i+1] == ':':
                bytes += "0a"
                i = i+1
            else:
                temp = hex(ord(text[i]))
                # print(temp)
                bytes += str(temp)[2:]
            i = i+1
        return bytes

    def encodeAllQuestions(qs):
        encoded_lists = []
        for i in range(len(qs)):
            encoded_lists.append(encodeQuestion(qs[i]))
        return encoded_lists

    def decryptNumberSecond (self, cm1, cm2):
        # temp = cm1**self.__a
        N2 = self.N*self.N
        temp = util.findMI(util.calculate_expo_mod(cm1, self.__a, N2), N2)
        # t = cm2/temp
        t = cm2*temp
        # print("t: ")
        # print(t)
        N2 = self.N*self.N
        m = ((t-1) % N2) // self.N
        # print(t-1 % N2)
        return m

    def getAverage (self, cm1, cm2, num):
        sum = self.decryptNumberSecond(cm1, cm2)
        return sum/num

    def decryptMatrixSecond(self, matrix1, matrix2):
        for i in range(len(matrix1)):
            for j in range(len(matrix1)):
                if i < j:
                    matrix1[i][j] = self.decryptNumberSecond(matrix1[i][j], matrix2[i][j])
                    matrix1[j][i]= matrix1[i][j]
        self.matrix = matrix1
        return matrix1

    def orderNumbers(self, matrix):
        order = [i for i in range (len(matrix))]
        order = self.sort(matrix, order)
        return order

    def sort(self, matrix, arr):
        half = self.N//2
        if len(arr) == 0:
            return []
        if len(arr) == 1:
            return arr
        left = []
        right = []
        mid = []
        mid.append(arr[0])
        for i in range(1, len(arr)):
            if (matrix[arr[0]][arr[i]] == 0 or matrix[arr[0]][arr[i]] <= half): # participants' answer: arr[0] > arr[i]
                left.append(arr[i])
            else:
                right.append(arr[i])
        left = self.sort(matrix, left)
        right = self.sort(matrix, right)
        return left + mid + right

    def getTopK(self, k, matrix1, matrix2):
        self.decryptMatrixSecond(matrix1, matrix2)
        order = self.orderNumbers(self.matrix)
        # request for (len(order)-k)-th participant's answer
        return order[len(order)-k]

    def getLastK(self, k, matrix1, matrix2):
        self.decryptMatrixSecond(matrix1, matrix2)
        order = self.orderNumbers(self.matrix)
        return order[k-1]

    def getMultipleChoiceCounting(self, cm1, cm2, k, x):
        num = self.decryptNumberSecond(cm1, cm2)
        count = []
        for i in range(x):
            temp = num & (2**k-1)
            num = num >> k
            count = [temp] + count
        return count

def issueQuestionnaire(contract_instance):
    print("question title:")
    title = str(input())
    title = Web3.toBytes(text=title)
    print("question content: ")
    content = str(input())
    content = Web3.toBytes(text=content)
    print("question types (use comma to separate)")
    types = str(input()).replace(' ', '')
    types = types.split(',')
    for i in range(len(types)):
        types[i] = int(types[i])
    question_count = len(types)
    tx_hash = contract_instance.addQuestionnaire(content, title, types, question_count, public_key_list, transact={'from':w3.eth.accounts[2]})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

if __name__=="__main__":
    with open("data.json", 'r') as f:
        datastore = json.load(f)
        config = datastore
    contract_instance = w3.eth.contract(address=config['contract_address'], abi=config['abi'], ContractFactoryClass=ConciseContract)
    NList = util.readBigIntFromContract(contract_instance, "N")
    gList = util.readBigIntFromContract(contract_instance, "g")
    h2List = util.readBigIntFromContract(contract_instance, "h2")
    N = util.mergeToBigInt(NList)
    g = util.mergeToBigInt(gList)
    h2 = util.mergeToBigInt(h2List)

    qp = QP(N, g, h2)
    qp.generateQPKeys()
    public_key = qp.getPublicKey()
    public_key_list = util.splitBigInt(public_key)
    while True:
        print("Choose what you want to do: ")
        print("1. issue questionnaire")
        print("2. ask for result of a questionnaire")
        print("3. ask for result of a participant with specific questionnaire and question")
        choice = int(input())
        if choice == 1:
            issueQuestionnaire(contract_instance)
        elif choice == 2:
            questionnaire_count = contract_instance.questionnaireCount()
            if questionnaire_count < 1:
                print("no existing questionnaire now")
                continue
            for i in range(1, question_count+1):
                print(str(i) + ". " + contract_instance.questionnaires[i].questionTitle())
            print("which questionnaire?")
            id = int(input())
            tx_hash = contract_instance.requireMining(id)
