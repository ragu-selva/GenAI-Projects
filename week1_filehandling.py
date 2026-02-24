####################### File Handling in Python #######################
# Writing to a file
print("Writing to example.txt...")
with open("example.txt", "w") as file:
    file.write("Hello, this is a sample file.\n")
    file.write("This file is used to demonstrate file handling in Python.\n")
print("Data has been written to example.txt")

# Reading from a file
print("Reading from example.txt...")
with open("example.txt", "r") as file:
    content = file.read()
    print("The content of example.txt is:\n" + content)
print("Data has been read from example.txt")
print(f"file content::::::: {content}")

# Appending to a file
print("Appending to example.txt...")
with open("example.txt", "a") as file:
    file.write("This line is appended to the file.\n")
print("Data has been appended to example.txt")

# Reading the updated file
print("Reading the updated example.txt...")
with open("example.txt", "r") as file:
    updated_content = file.read()
    print("The updated content of example.txt is:\n" + updated_content)
print("Data has been read from example.txt")

# Handling file not found error
print("Trying to read a non-existent file...")
try:
    with open("non_existent_file.txt", "r") as file:
        content = file.read()
        print("The content of non_existent_file.txt is:\n" + content)
except FileNotFoundError:
    print("Error: The file non_existent_file.txt was not found")
    
  
  
  ############################# OS commands for file handling #############################
print("Using OS commands to handle files...")
import os
# Create a new directory
print("Creating a new directory called 'test_directory'...")
#if directory already exists, this will raise a FileExistsError, so we can handle that as well
try:
    os.mkdir("test_directory")
except FileExistsError:
    print("Directory 'test_directory' already exists")
# Change the current working directory
print("Changing the current working directory to 'test_directory'...")
os.chdir("test_directory")
print("Current working directory is now: " + os.getcwd())
# Create a new file in the new directory
print("Creating a new file called 'test_file.txt' in 'test_directory'...")
with open("test_file.txt", "w") as file:
    file.write("This is a test file created using OS commands.\n")
print("File 'test_file.txt' has been created in 'test_directory'")
# List files in the current directory
print("Listing files in the current directory...")
files = os.listdir()
print("Files in the current directory: " + str(files))

