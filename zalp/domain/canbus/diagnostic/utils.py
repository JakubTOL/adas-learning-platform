def iterable_data_to_str(data):
    return ' '.join(format(x, '02X') for x in data)
