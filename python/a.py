data = [{'pattern-inside': '$QUERY = $SQL + $VAL\n...\n'}, {'pattern': '$CONNECTION.execute($QUERY, ...)\n'}]

# Initialize an empty string to store the result
result = ""

for item in data:
    if 'pattern-inside' in item.keys and 'pattern' in item.keys:
        print("hey")
        pattern_inside = item['pattern-inside']
        pattern = item['pattern']
        
        # Find the last occurrence of '\n' in pattern_inside
        last_newline_index = pattern_inside.rfind('\n')
        print(last_newline_index)
        
        # Append pattern after the before last '\n'
        result += pattern_inside[:last_newline_index] + pattern + '\n' + pattern_inside[last_newline_index:]

# Print the result
print(result)