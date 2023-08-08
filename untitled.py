import collections

# Define the dictionary
dict = {"Staves":[1,2,3], "Modules":[2,7,9], "Towers":[55, 67, 9]}

# List of keys in the order you want to iterate
keys = ["Staves", "Modules", "Towers"]

def nested_loops(dict, keys, combinations =None, values={}):
        if combinations is None:
            combinations = []
        if keys:
            current_key = keys[0]
            remaining_keys = keys[1:]
            for value in dict.get(current_key, []):
                new_values = values.copy()
                new_values[current_key] = value
                nested_loops(dict, remaining_keys, combinations, new_values)
        else:
            combinations.append(values)
        return combinations

print(nested_loops(dict, keys))
