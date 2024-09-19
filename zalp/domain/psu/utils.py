def voltage_format(voltage):
    if float(voltage).is_integer():
        ret = voltage
    else:
        ret = round(voltage, 2)
    return str(ret)


def voltage_ok(voltage):
    # TODO: implement voltage limits here as actual on the used KORAD unit
    return 0.0 <= voltage <= 50.0
