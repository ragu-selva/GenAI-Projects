#####################  1:   List Comprehensions  #####################

print("************************1.  List Comprehensions  ************************")
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
print("The original list of fruits is " + str(fruits))

# Create a new list with the lengths of each fruit name
fruit_lengths = [len(fruit) for fruit in fruits]
print("The lengths of each fruit name are " + str(fruit_lengths))
print("adding 1 to each length")
fruit_lengths_plus_one = [length + 1 for length in fruit_lengths]
print("The lengths of each fruit name plus one are " + str(fruit_lengths_plus_one))

# Create a new list with only the fruits that have more than 5 letters
long_fruits = [fruit for fruit in fruits if len(fruit) > 5]
print("The fruits with more than 5 letters are " + str(long_fruits))

#add new fruit to the list
fruits.append("fig")
print("The updated list of fruits is " + str(fruits))

#remove a fruit from the list
fruits.remove("banana")
print("The updated list of fruits after removing banana is " + str(fruits)) 

#add duplicate fruit to the list
fruits.append("apple")
print("The updated list of fruits after adding duplicate apple is " + str(fruits))

#get the index of a fruit in the list
index_of_cherry = fruits.index("cherry")
print("The index of cherry in the list is " + str(index_of_cherry))

#get index of a fruit that is not in the list
try:
    index_of_orange = fruits.index("orange")
    print("The index of orange in the list is " + str(index_of_orange))
except ValueError:
    print("Orange is not in the list of fruits")
    
print("The number of times apple appears in the list is " + str(fruits.count("apple")))


######################### 2:  Tuples  ########################
print("************************2.  Tuples  ************************")
# Create a tuple of fruits
fruit_tuple = ("apple", "banana", "cherry", "date", "elderberry")
print("The original tuple of fruits is " + str(fruit_tuple))
# Create a new tuple with the lengths of each fruit name
fruit_tuple_lengths = tuple(len(fruit) for fruit in fruit_tuple)
print("The lengths of each fruit name in the tuple are " + str(fruit_tuple_lengths))
# Create a new tuple with only the fruits that have more than 5 letters
long_fruit_tuple = tuple(fruit for fruit in fruit_tuple if len(fruit) > 5)
print("The fruits with more than 5 letters in the tuple are " + str(long_fruit_tuple))
# Get the index of a fruit in the tuple
index_of_cherry_tuple = fruit_tuple.index("cherry")
print("The index of cherry in the tuple is " + str(index_of_cherry_tuple))
#add new fruit to the tuple (tuples are immutable, so we need to create a new tuple)
new_fruit_tuple = fruit_tuple + ("fig",)
print("The updated tuple of fruits after adding fig is " + str(new_fruit_tuple))

#check tuple immutability by trying to change an element (this will raise an error)
try:
    fruit_tuple[0] = "grape"
except TypeError:
    print("Tuples are immutable, cannot change an element")
    
#check if a fruit is in the tuple
is_banana_in_tuple = "banana" in fruit_tuple
print("Is banana in the tuple? " + str(is_banana_in_tuple))


########################### 3:  Sets  ########################
print("************************3.  Sets  ************************")
# Create a set of fruits
fruit_set = {"apple", "banana", "cherry", "date", "elderberry"}
print("The original set of fruits is " + str(fruit_set))
# Create a new set with the lengths of each fruit name
fruit_set_lengths = {len(fruit) for fruit in fruit_set}
print("The lengths of each fruit name in the set are " + str(fruit_set_lengths))
# Create a new set with only the fruits that have more than 5 letters
long_fruit_set = {fruit for fruit in fruit_set if len(fruit) > 5}
print("The fruits with more than 5 letters in the set are " + str(long_fruit_set))

#add new fruit to the set
fruit_set.add("fig")
print("The updated set of fruits after adding fig is " + str(fruit_set))
#remove a fruit from the set
fruit_set.remove("banana")
print("The updated set of fruits after removing banana is " + str(fruit_set))
#add duplicate fruit to the set (sets do not allow duplicates, so this will not change the set)
fruit_set.add("apple")
print("The updated set of fruits after adding duplicate apple is " + str(fruit_set))
#get the number of fruits in the set
number_of_fruits_in_set = len(fruit_set)
print("The number of fruits in the set is " + str(number_of_fruits_in_set))
#check if a fruit is in the set
is_cherry_in_set = "cherry" in fruit_set
print("Is cherry in the set? " + str(is_cherry_in_set))

#check if a fruit is not in the set
is_orange_not_in_set = "orange" not in fruit_set
print("Is orange not in the set? " + str(is_orange_not_in_set))

#check index of a fruit in the set (this will raise an error because sets do not have indices)
try:
    index_of_cherry_in_set = fruit_set.index("cherry")
except AttributeError:
    print("Sets do not have indices, cannot get index of a fruit in the set")
    


########################### 4. Dictionaries  ########################
print("************************4.  Dictionaries  ************************") 
# Create a dictionary of fruits and their colors
fruit_colors = {"apple": "red", "banana": "yellow", "cherry": "red", "date": "brown", "elderberry": "purple"}
print("The original dictionary of fruits and their colors is " + str(fruit_colors))
# Create a new dictionary with the lengths of each fruit name as keys and the fruit names as values
fruit_length_dict = {len(fruit): fruit for fruit in fruit_colors.keys()}
print("The dictionary with lengths of fruit names as keys and fruit names as values is " + str(fruit_length_dict))
#fetch the color of a fruit from the dictionary
color_of_cherry = fruit_colors["cherry"]
print("The color of cherry is " + color_of_cherry)
#add a new fruit and its color to the dictionary
fruit_colors["fig"] = "purple"
print("The updated dictionary of fruits and their colors after adding fig is " + str(fruit_colors))
#remove a fruit from the dictionary
del fruit_colors["banana"]
print("The updated dictionary of fruits and their colors after removing banana is " + str(fruit_colors))
#update the color of a fruit in the dictionary
fruit_colors["apple"] = "green"
print("The updated dictionary of fruits and their colors after changing apple color to green is " + str(fruit_colors))
#check if a fruit is in the dictionary
is_date_in_dict = "date" in fruit_colors
print("Is date in the dictionary? " + str(is_date_in_dict))
#check if a fruit is not in the dictionary
is_orange_not_in_dict = "orange" not in fruit_colors
print("Is orange not in the dictionary? " + str(is_orange_not_in_dict))
#get the number of fruits in the dictionary
number_of_fruits_in_dict = len(fruit_colors)
print("The number of fruits in the dictionary is " + str(number_of_fruits_in_dict))


