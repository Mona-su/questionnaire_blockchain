import random
from Crypto.Util import number
from Crypto.Random import random
import sys
import util

# set recursion  limit to be large enough
sys.setrecursionlimit(5000)

def generateKeys(bits):
    p = number.getPrime(bits) # p and q are still int, can do calculations
    q = number.getPrime(bits)
    # p = 5
    # q = 7
    print(p)
    print(q)
    N = p*q
    N2 = N*N
    u = 0
    while (True):
        u = random.randint(0, N2)
        if (number.GCD(u, N2) == 1):
            break
    # print("u:")
    # print(u)
    g = util.calculate_expo_mod (-u, 2*N, N2)
    # g = -(u*u)%N2
    return g, N

# g, N = generateKeys()
# print(g)
# print(N)
