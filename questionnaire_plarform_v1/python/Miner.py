from Crypto.Util import number
from Crypto.Random import random
import sys
import util

class Miner:
    def __init__(self, N):
        self.N = N

    def multiply(cm1_list, cm2_list):
        N2 = self.N*self.N
        cm1 = 1
        cm2 = 1
        for i in range(len(cm1_list)):
            cm1 = (cm1*cm1_list[i]) % N2
            cm2 = (cm2*cm2_list[i]) % N2
        return cm1, cm2

    def buildCell(self, cmi1, cmi2, cmj1, cmj2):
        f = random.randint(1, int((self.N//2)**0.5))
        N2 = self.N*self.N
        N = self.N
        temp1 = util.calculate_expo_mod(cmj1, N-1, N2)
        temp1 = (temp1*cmi1)%N2
        temp1 = util.calculate_expo_mod(temp1, f, N2)
        temp2 = util.calculate_expo_mod(cmj2, N-1, N2)
        temp2 = (temp2*cmi2)%N2
        temp2 = util.calculate_expo_mod(temp2, f, N2)
        return temp1, temp2

    def buildMatrix(self, list1, list2): # input: a list of nums
        matrix1 = [[] for i in range(len(list1))]
        matrix2 = [[] for i in range(len(list1))]
        for i in range(len(list1)):
            matrix1[i] = [0 for i in range(len(list1))]
            matrix2[i] = [0 for i in range(len(list1))]
            for j in range(len(list1)):
                if i < j:
                    matrix1[i][j], matrix2[i][j] = self.buildCell(list1[i], list2[i], list1[j], list2[j])
        return matrix1, matrix2
