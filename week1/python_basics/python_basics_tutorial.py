# Python Basics Tutorial for Beginners
# -----------------------------------
# This program covers all fundamental Python concepts with explanations.

# 1. Print Statements and Comments
print("Hello, World!  # This is a print statement.")  # This is a comment

# 2. Variables and Data Types
name = "Alice"  # String
age = 25        # Integer
height = 5.6    # Float
is_student = True  # Boolean
print("Name:", name)
print("Age:", age)
print("Height:", height)
print("Is student?", is_student)

# 3. Operators
x = 10
y = 3
print("Addition:", x + y)
print("Subtraction:", x - y)
print("Multiplication:", x * y)
print("Division:", x / y)
print("Floor Division:", x // y)
print("Modulus:", x % y)
print("Exponentiation:", x ** y)
print("Comparison:", x > y)
print("Logical AND:", x > 5 and y < 5)

# 4. Input/Output
# Uncomment the next two lines to try input
# user_name = input("Enter your name: ")
# print("Hello,", user_name)

# 5. Conditional Statements
if age < 18:
    print("You are a minor.")
elif age < 65:
    print("You are an adult.")
else:
    print("You are a senior citizen.")

# 6. Loops
print("\nFor loop:")
for i in range(5):
    print(i)

print("\nWhile loop:")
count = 0
while count < 3:
    print(count)
    count += 1

# 7. Functions
def greet(person):
    print(f"Hello, {person}!")

greet("Bob")

def add(a, b):
    return a + b

result = add(5, 7)
print("Sum:", result)

# 8. Data Structures
# List
fruits = ["apple", "banana", "cherry"]
print("List:", fruits)
fruits.append("orange")
print("After append:", fruits)

# Tuple
colors = ("red", "green", "blue")
print("Tuple:", colors)

# Set
unique_numbers = {1, 2, 3, 2}
print("Set:", unique_numbers)

# Dictionary
details = {"name": "Alice", "age": 25}
print("Dictionary:", details)
print("Name from dict:", details["name"])

# 9. File Handling
# Writing to a file
with open("sample.txt", "w") as f:
    f.write("This is a sample file.\n")
    f.write("Python file handling example.\n")

# Reading from a file
with open("sample.txt", "r") as f:
    content = f.read()
    print("\nFile content:")
    print(content)

# 10. Exception Handling
try:
    num = int("abc")  # This will raise ValueError
except ValueError as e:
    print("Error:", e)
finally:
    print("Exception handling complete.")

# 11. Classes and Objects
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def say_hello(self):
        print(f"Hi, I'm {self.name} and I'm {self.age} years old.")

person1 = Person("Charlie", 30)
person1.say_hello()

# 12. Importing Modules
import math
print("Square root of 16:", math.sqrt(16))

# End of tutorial
print("\nCongratulations! You have learned Python basics.")
