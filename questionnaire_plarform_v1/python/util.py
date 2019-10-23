import sys

sys.setrecursionlimit(5000)

# calculate (u**(expo)))%(mod)
def calculate_expo_mod (u, expo, mod):
    if expo > 0:
        half = expo // 2
        remainder = expo % 2
        cal = calculate_expo_mod (u, half, mod)
        ans = (cal*cal*(u**remainder)) % (mod)
        # print(cal*cal*(u**remainder))
        return ans
    return 1

#欧几里得算法求最大公约数
def get_gcd(a, b):
    k = a // b
    remainder = a % b
    while remainder != 0:
    	a = b
    	b = remainder
    	k = a // b
    	remainder = a % b
    return b

#改进欧几里得算法求线性方程的x与y
def get_(a, b):
	if b == 0:
		return 1, 0
	else:
		k = a // b
		remainder = a % b
		x1, y1 = get_(b, remainder)
		x, y = y1, x1 - k * y1
	return x, y

# b is N (or N^2)
def findMI(a, b):
    # a, b = input().split()
    # a, b = int(a), int(b)

    #将初始b的绝对值进行保存
    if b < 0:
    	m = abs(b)
    else:
    	m = b
    flag = get_gcd(a, b)
    print("flag: ")
    print(flag)

    #判断最大公约数是否为1，若不是则没有逆元
    x0 = -1
    if flag == 1:
    	x, y = get_(a, b)
    	x0 = x % m #对于Python '%'就是求模运算，因此不需要'+m'
    	print("x0:",x0) #x0就是所求的逆元
    else:
    	print("Do not have!")
    return x0
#
#  ————————————————
# 版权声明：本文为CSDN博主「up中的小猿类」的原创文章，遵循CC 4.0 by-sa版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/baidu_38271024/article/details/78881031
