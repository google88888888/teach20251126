b = "default"
c = 'default'
d = "default"
e = "default"
f = "default"
g = "default"
import random

num = [1,2,3,4,5,6,7,8,9,10,11,12,13]

picked = random.choice(num)
num.remove(picked)

picked2 = random.choice(num)
num.remove(picked2)

picked3 = random.choice(num)
num.remove(picked3)

picked4 = random.choice(num)
num.remove(picked4)

print(picked,picked2,picked3,picked4)

correctNumber=[picked,picked2,picked3,picked4]

while True:
    a = input("your solution's first number:")
    if a.isdigit() and int(a) in correctNumber:
        num2 = int(a)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

while True:
    b = input("+-*/:")
    if b in ("+", "-", "*", "/"):
        break
    else:
        print("this can only be +,-,*,/")
        

while True:
    c = input("your solution's second number:")
    if c.isdigit()  and int(c) in correctNumber:
        num3 = int(c)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)


while True:
    d = input("+-*/:")
    if d in ("+", "-", "*", "/"):
        break
    else:
        print("this can only be +,-,*,/")


while True:
    e = input("your solution's third number:")
    if e.isdigit() and int(e) in correctNumber:
        num4 = int(e)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

    
while True:
    f = input("+-*/:")
    if f in ("+", "-", "*", "/"):
        break
    else:
        print("this can only be +,-,*,/")


while True:
    g = input("your solution's fourth number:")
    if g.isdigit() and int(g) in correctNumber:
        num5 = int(g)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

totalString = str(num2)+b+str(num3)+d+str(num4)+f+str(num5)
total=eval(totalString)

print(total,'total')
if total == 24:
    print("you did it!!!")

else:
    print("that was the wrong way")