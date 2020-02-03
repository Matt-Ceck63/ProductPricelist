def format_num(number, is_string=False):
    # NOTE: this does not check if all digits are 0


    if not is_string:
        number = str(number)

    if len(number) > 7:
        number = number[:7]

    if '.' in number:
        dec_length = len(number.split('.')[1])
        if dec_length < 2:
            number += '0'
    else:
        number += '.00'

    # Insert commas
    if ',' not in number and len(number) > 6:
        threes = int((len(number) - 3) / 3)
        index = (len(number) - 3) % 3
        for i in range(0, threes):
            if index != 0:
                index += (i * 3)
                number = number[:index + i] + ',' + number[index + i:]

    return number

def to_float(val):
    try:
        val = float(val)
    except ValueError:
        val = val.replace(",", "")
        val = val[:val.find(".")]
        try:
            val = float(val)
        except ValueError:
            pass
    return val