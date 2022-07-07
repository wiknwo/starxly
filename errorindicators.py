def indicate_error(text, position_start, position_end):
    """Function to indicate to user exactly where error occurred using string with arrows pointing at sources of error"""
    result = ''
    # Calculate indices
    start_index = max(text.rfind('\n', 0, position_start.index), 0)
    end_index = text.find('\n', start_index + 1)
    if end_index < 0:
        end_index = len(text)
    # Generate each line
    line_count = position_end.line_number - position_start.line_number + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[start_index:end_index]
        start_column_index = position_start.column_number if i == 0 else 0
        end_column_index = position_end.column_number if i == line_count - 1 else len(line) - 1
        # Append to result
        result += line + '\n'
        result += ' ' * start_column_index + '^' * (end_column_index - start_column_index)
        # Re-calculate indices
        start_index = end_index
        end_index = text.find('\n', start_index + 1)
        if end_index < 0:
            end_index = len(text)
    return result.replace('\t', '')