from Crypto.Util import number
from Crypto.Random import random
import sys
import util

sys.setrecursionlimit(5000)

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
