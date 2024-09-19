import cantools


def parse_dbc(path):
    dbc = cantools.database.load_file(path)
    return dbc
