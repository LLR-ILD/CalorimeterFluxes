import collections

# Define the dictionary
dict = {"Staves":[1,2,3], "Modules":[2,7,9], "Towers":[55, 67, 9]}

# List of keys in the order you want to iterate
keys = ["Staves", "Modules", "Towers"]

# List to store the combinations where the second value equals 2
combinations = []

# Function to perform the nested loops
def nested_loops(dict, keys, values={}):
    if keys:
        current_key = keys[0]
        remaining_keys = keys[1:]
        for value in dict.get(current_key, {}):
            values[current_key] = value
            nested_loops(dict, remaining_keys, values)
    else:
        # If the second value equals 2, add the values to the combinations list
        print(values)

# Call the function
nested_loops(dict, keys)
