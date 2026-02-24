print("Hi... Welcome to Python programming!")

name = "ragu"
print("My name is " + name)

########################operators###############

a = 10
b = 3

print("************************Arithmetic Operators************************")
print("The value of a is " + str(a))
print("The value of b is " + str(b))
add = a+b
print("The addition of a and b is " + str(add))
sub = a-b
print("The subtraction of a and b is " + str(sub))
mul = a*b
print("The multiplication of a and b is " + str(mul))
div = a/b
print("The division of a and b is " + str(div))
mod = a%b
print("The modulus of a and b is " + str(mod))
exp = a**b
print("The exponent of a and b is " + str(exp))
floor_div = a//b
print("The floor division of a and b is " + str(floor_div))


#################Comaprison operators##################

x = 5
y = 3

print("************************Comparison Operators************************")
print("The value of x is " + str(x))
print("The value of y is " + str(y))
print("Is x equal to y? " + str(x == y))
print("Is x not equal to y? " + str(x != y))
print("Is x greater than y? " + str(x > y))
print("Is x less than y? " + str(x < y))
print("Is x greater than or equal to y? " + str(x >= y))
print("Is x less than or equal to y? " + str(x <= y))

#########################Logical operators######################
c = 4
d = 6
print("************************Logical Operators************************")
print("The value of c is " + str(c))
print("The value of d is " + str(d))
print("Is c greater than 3 and d less than 10? " + str(c > 3 and d < 10))
print("Is c greater than 5 or d less than 5? " + str(c > 5 or d < 5))
print("Is c not greater than 3? " + str(not (c > 3)))

##########################Assignment operators######################
e = 10
print("************************Assignment Operators************************")
print("The initial value of e is " + str(e))
e += 5
print("After adding 5, the value of e is " + str(e))
e -= 3
print("After subtracting 3, the value of e is " + str(e))
e *= 2
print("After multiplying by 2, the value of e is " + str(e))
e /= 4
print("After dividing by 4, the value of e is " + str(e))
e %= 3
print("After modulus by 3, the value of e is " + str(e))

########################### Membership operators######################
list = [1, 2, 3, 4, 5]
print("************************Membership Operators************************")
print("Is 3 in the list? " + str(3 in list))
print("Is 6 in the list? " + str(6 in list))
print("Is 7 not in the list? " + str(7 not in list))

########################### Identity operators######################
f = 10
g = 10
h = 20
print("************************Identity Operators************************")
print("Are f and g identical? " + str(f is g))
print("Are f and h identical? " + str(f is h))
print("Are f and g not identical? " + str(f is not g))