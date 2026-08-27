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

totalString=''

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    a = input("your solution's first number:")
    if a.isdigit() and int(a) in correctNumber:
        num2 = int(a)
        totalString = totalString+str(num2)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    b = input("+-*/:")
    if b in ("+", "-", "*", "/"):
        totalString = totalString+str(b)
        break
    else:
        print("this can only be +,-,*,/")
        
while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    c = input("your solution's second number:")
    if c.isdigit()  and int(c) in correctNumber:
        num3 = int(c)
        totalString = totalString+str(num3)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    d = input("+-*/:")
    if d in ("+", "-", "*", "/"):
        totalString = totalString+str(d)
        break
    else:
        print("this can only be +,-,*,/")

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    e = input("your solution's third number:")
    if e.isdigit() and int(e) in correctNumber:
        num4 = int(e)
        totalString = totalString+str(num4)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)


while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    f = input("+-*/:")
    if f in ("+", "-", "*", "/"):
        totalString = totalString+str(f)
        break
    else:
        print("this can only be +,-,*,/")

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

while True:
    g = input("your solution's fourth number:")
    if g.isdigit() and int(g) in correctNumber:
        num5 = int(g)
        totalString = totalString+str(num5)
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)

while True:
    g = input("( or ) or or no:")
    if g=='no':
        break
    elif g in ("(", ")"):
        totalString = totalString+str(g)
        break
    else: 
        print("this can only be ( or ) or or no")

total=eval(totalString)

print(total,'total')
if total == 24:
    print("you did it!!!")

else:
    print("that was the wrong way")