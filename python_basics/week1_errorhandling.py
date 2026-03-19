######################### Error Handling in Python #########################
# Example of handling a ZeroDivisionError
try:
    a = 10
    b = 0
    result = a / b
    print("The result of division is " + str(result))   
except ZeroDivisionError:
    print("Error: Division by zero is not allowed")

# Example of handling a ValueError
try:
    user_input = input("Enter a number: ")
    user_number = float(user_input)
    print("The user entered the number " + str(user_number))
except ValueError:
    print("Error: Invalid input, please enter a valid number")
finally:
    print("This block will always be executed, regardless of whether an error occurred or not")

# Example of handling a FileNotFoundError
try:
    with open("non_existent_file.txt", "r") as file:
        content = file.read()
        print("The content of the file is: " + content)
except FileNotFoundError:
    print("Error: The file was not found")