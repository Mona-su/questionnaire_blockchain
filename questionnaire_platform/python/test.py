from Crypto.Util import number
from Crypto.Random import random
import sys
import util
import QP
import SQS
import Miner
import generateKey as gk
import participant

sys.setrecursionlimit(5000)

m = 8
mlist = [7, 8, 9, 6]
g, N = gk.generateKeys(512)
N2 = N*N
print("g: ")
print(g)
print(util.splitBigInt(g))
print("N: ")
print(N)
print(util.splitBigInt(N))
sqs = SQS.SQS(N, g)
sqs.generateSQSKeys()
print(3)
h2 = sqs.getSQSPublicKey()
print(util.splitBigInt(h2))
print(4)
qp = QP.QP(N, g, h2)
print(5)
qp.generateQPKeys()
print(6)
h1 = qp.getQPPublicKey()
print(7)
h = h1*h2
print(8)
miner = Miner.Miner(N)

def testOne(m):
    par = participant.Participant(g, N, h)
    cm1, cm2 = par.encryption(m)
    print("cm1: ")
    print(cm1)
    print("cm2: ")
    print(cm2)
    cm1prime, cm2prime = sqs.decryptNumberFirst(cm1, cm2)
    print("cm1prime: ")
    print(cm1prime)
    print("cm2prime: ")
    print(cm2prime)
    decryptedM = qp.decryptNumberSecond(cm1prime, cm2prime)
    print("decrypted message: ")
    print(decryptedM)

def testMultiplication():
    cm1 = 1
    cm2 = 1
    m = [7, 8, 9, 8, 6, 8]
    for i in range(6):
        par1 = participant.Participant(g, N, h)
        cmi1, cmi2 = par1.encryption(m[i])
        cm1 = (cm1*cmi1) % N2
        cm2 = (cm2*cmi2) % N2
    print("cm1: ")
    print(cm1)
    print("cm2: ")
    print(cm2)
    cm1prime, cm2prime = sqs.decryptNumberFirst(cm1, cm2)
    print("cm1prime: ")
    print(cm1prime)
    print("cm2prime: ")
    print(cm2prime)
    # decryptedM = qp.decryptNumberSecond(cm1prime, cm2prime)
    # print("decrypted message: ")
    # print(decryptedM)
    avg = qp.getAverage(cm1prime, cm2prime, 6)
    print("average: ")
    print(avg)

def comparison(mi, mj):
    par1 = participant.Participant(g, N, h)
    cmi1, cmi2 = par1.encryption(mi)
    par2 = participant.Participant(g, N, h)
    cmj1, cmj2 = par1.encryption(mj)
    f = random.randint(1, int((N//2)**0.5))
    temp1 = util.calculate_expo_mod(cmj1, N-1, N2)
    temp1 = (temp1*cmi1)%N2
    temp1 = util.calculate_expo_mod(temp1, f, N2)
    temp2 = util.calculate_expo_mod(cmj2, N-1, N2)
    temp2 = (temp2*cmi2)%N2
    temp2 = util.calculate_expo_mod(temp2, f, N2)
    print("cm1: ")
    print(temp1)
    print("cm2: ")
    print(temp2)
    cm1prime, cm2prime = sqs.decryptNumberFirst(temp1, temp2)
    print("cm1prime: ")
    print(cm1prime)
    print("cm2prime: ")
    print(cm2prime)
    decryptedM = qp.decryptNumberSecond(cm1prime, cm2prime)
    print("decrypted message: ")
    print(decryptedM)

def testMatrix(mlist):
    encrypted1 = [0 for i in range(len(mlist))]
    encrypted2 = [0 for i in range(len(mlist))]
    for i in range(len(mlist)):
        par = participant.Participant(g, N, h)
        encrypted1[i], encrypted2[i] = par.encryption(mlist[i])
    matrix1, matrix2 = miner.buildMatrix(encrypted1, encrypted2)
    matrix1, matrix2 = sqs.decryptMatrixFirst(matrix1, matrix2)
    # matrix = qp.decryptMatrixSecond(matrix1, matrix2)
    # order = qp.orderNumbers(matrix)
    ans = qp.getLastK(2, matrix1, matrix2)
    print(ans)

def testMultipleChoice(list, x):
    par = participant.Participant(g, N, h)
    cm1, cm2 = par.encryptMultipleChoice(list, x)
    print("cm1: ")
    print(cm1)
    print("cm2: ")
    print(cm2)
    cm1prime, cm2prime = sqs.decryptNumberFirst(cm1, cm2)
    print("cm1prime: ")
    print(cm1prime)
    print("cm2prime: ")
    print(cm2prime)
    decryptedM = qp.getMultipleChoiceCounting(cm1prime, cm2prime, x, len(list))
    print("decrypted message: ")
    print(decryptedM)

def testSplitBigNum():
    print("N2: ")
    print(len(bin(N2)))
    print(bin(N2))
    print(hex(N2))
    list = util.splitBigInt(N2)
    for i in range(len(list)):
        print("list[" + str(i) + "]")
        print(hex(list[i]))
    num = util.mergeToBigInt(list)
    print("num: ")
    print(hex(num))
    print(num==N2)

# testMultiplication()
# testOne(N//2+10)
# comparison(8, 8)
# testMatrix(mlist)
# testOne(5)
testSplitBigNum()
# mlist = [0, 1, 1, 0]
# k = 5
# testMultipleChoice(mlist, k)
