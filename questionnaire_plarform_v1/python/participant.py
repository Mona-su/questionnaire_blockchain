from Crypto.Util import number
from Crypto.Random import random
import sys
import util

sys.setrecursionlimit(2500)

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
            if list[i] == 1:
                ans = ans | 1
        print("bit representation of answers: ")
        print(ans)
        print(bin(ans))
        return self.encryption(ans)
