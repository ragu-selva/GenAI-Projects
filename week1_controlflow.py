##################### Control flow statements #####################
print("************************1.  Control flow statements  ************************")
# If statement
x = 10
print("The value of x is " + str(x))
if x > 5:
    print("x is greater than 5")
# If-else statement
y = 3
print("The value of y is " + str(y))
if y > 5:
    print("y is greater than 5")
else:
    print("y is not greater than 5")    
# If-elif-else statement
z = 7
print("The value of z is " + str(z))
if z > 10:
    print("z is greater than 10")
elif z > 5:
    print("z is greater than 5 but not greater than 10")
else:
    print("z is not greater than 5")


########################## NEsted if statements ######################
print("************************2.  Nested if statements  ************************")
a = 15
print("The value of a is " + str(a))
if a > 10:
    print("a is greater than 10")
    if a % 2 == 0:
        print("a is even")
    else:
        print("a is odd")

#check if a number is positive, negative or zero
b = -5
print("The value of b is " + str(b))
if b > 0:
    print("b is positive")
    if b % 2 == 0:
        print("b is even")  
    else:
        print("b is odd")   
else:
    print("b is negative or zero")

# get the user input and check if it is a positive or negative number
user_input = 50 #input("Enter a number: ")
try:
    user_number = float(user_input)
    print("The user entered the number " + str(user_number))
    if user_number > 0:
        print("The number is positive")
    elif user_number < 0:
        print("The number is negative")
    else:
        print("The number is zero")
except ValueError:
    print("Invalid input, please enter a valid number")


####################### For loop with if statement ######################
print("************************3.  For loop with if statement  ************************")
# Print all the even numbers from a list
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("The original list of numbers is " + str(numbers))
print("The even numbers in the list are: ")
for number in numbers:
    if number % 2 == 0:
        print(number)
# Print all the fruits that have more than 5 letters in a list
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
print("The original list of fruits is " + str(fruits))
print("The fruits with more than 5 letters in the list are: ")
for fruit in fruits:
    if len(fruit) > 5:
        print(fruit)
# Print all the numbers that are divisible by 3 in a list
print("The numbers that are divisible by 3 in the list are: ")
for number in numbers:
    if number % 3 == 0:
        print(number)

######################### While loop with if statement ######################
print("************************4.  While loop with if statement  ************************")
# Print the numbers from 1 to 10 and check if they are even or odd
i = 1
print("The numbers from 1 to 10 and their even/odd status are: ")
while i <= 10:
    if i % 2 == 0:
        print(str(i) + " is even")
    else:
        print(str(i) + " is odd")
    i += 1

# Get user input until they enter a positive number
user_input =  int(input("Enter a positive number: "))      
while user_input <= 0:
    try:
        user_input = float(user_input)
        if user_input > 0:
            print("Thank you for entering a positive number: " + str(user_input))
        else:
            print("Please enter a positive number: ")
            user_input = int(input("Enter a positive number: ")) #reset to continue the loop
    except ValueError:
        print("Invalid input, please enter a valid number: ")
        user_input = int(input("Enter a positive number: ")) #reset to continue the loop     







