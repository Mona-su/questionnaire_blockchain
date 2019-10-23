from Crypto.Util import number
from Crypto.Random import random
import sys
import util

sys.setrecursionlimit(5000)

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
