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
    if a.isdigit() and a in correctNumber:
        num2 = int(a)
        b = input("+-*/:")
        break
    else: 
        print("this can only be a number and this number should be one of ",picked,picked2,picked3,picked4)
    

if b in ("+", "-", "*", "/"):
    c = input("your solution's second number:")

elif b == ("default"):
    print(" ")

else:
    print("this can only be +,-,*,/")

if c.isdigit()  and c in correctNumber:
    num3 = int(c)
    d = input("+-*/:")

elif c == ("default"):
    print(" ")


else: 
    print("this can only be a number and this number should be one of",picked,picked2,picked3,picked4)

if d in ("+", "-", "*", "/"):
    e = input("your solution's third number:")

elif d == ("default"):
    print(" ")

else:
    print("this can only be +,-,*,/")

if e.isdigit() and  e in correctNumber:
    num4 = int(e)
    f = input("+-*/:")
elif e == ("default"):
    print(" ")
else: 
    print("this can only be a number and this number should be one of",picked,picked2,picked3,picked4)

if f in ("+", "-", "*", "/"):
    g = input("your solution's fourth number:")
elif f == ("default"):
    print(" ")

else:
    print("this can only be +,-,*,/")

if g.isdigit() and g in correctNumber:
    num5 = int(g)
elif g == ("default"):
    print(" ")
else: 
    print("this can only be a number and this number should be one of",picked,picked2,picked3,picked4)

# total=num2

# if b =="+":
#     total = total + num3
# elif b=="-":
#     total = total - num3
# elif b=="*":
#     total = total * num3
# elif b=="/":
#     total = total / num3

# if d =="+":
#     total = total + num4
# elif d=="-":
#     total = total - num4
# elif d=="*":
#     total = total * num4
# elif d=="/":
#     total = total / num4

# if f =="+":
#     total = total + num5
# elif f=="-":
#     total = total - num5
# elif f=="*":
#     total = total * num5
# elif f=="/":
#     total = total / num5

totalString = str(num2)+b+str(num3)+d+str(num4)+f+str(num5)
total=eval(totalString)

print(total,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
if total == 24:
    print("you did it!!!")

else:
    print("that was the wrong way")