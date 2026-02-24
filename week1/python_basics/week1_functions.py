############################### functions ###############################

# Function to calculate the area of a rectangle
def calculate_rectangle_area(length, width):
    area = length * width
    return area

# Function to calculate the area of a circle
def calculate_circle_area(radius):
    import math
    area = math.pi * radius ** 2
    return area

# Function to calculate the area of a triangle
def calculate_triangle_area(base, height):
    area = 0.5 * base * height
    return area

# Function to calculate the area of a square
def calculate_square_area(side):
    area = side ** 2
    return area

#calling the functions and printing the results
length = 5
width = 3
rectangle_area = calculate_rectangle_area(length, width)
print("The area of the rectangle with length " + str(length) + " and width " + str(width) + " is " + str(rectangle_area))

radius = 4
circle_area = calculate_circle_area(radius)
print("The area of the circle with radius " + str(radius) + " is " + str(circle_area))

base = 6
height = 8
triangle_area = calculate_triangle_area(base, height)
print("The area of the triangle with base " + str(base) + " and height " + str(height) + " is " + str(triangle_area))

side = 7
square_area = calculate_square_area(side)
print("The area of the square with side " + str(side) + " is " + str(square_area))

#function with IF statement to check if the area of a rectangle is greater than a certain value
def is_rectangle_area_greater_than(length, width, value):
    area = calculate_rectangle_area(length, width)
    if area > value:
        return True
    else:
        return False

length = 5
width = 3
value = 10
result = is_rectangle_area_greater_than(length, width, value)
print("Is the area of the rectangle with length " + str(length) + " and width " + str(width) + " greater than " + str(value) + "? " + str(result))
