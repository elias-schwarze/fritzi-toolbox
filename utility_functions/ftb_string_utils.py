def strip_End_Numbers(inputString):
    """Strip trailing numbers and dot from string, if any"""
    if ("." in inputString[-4:] and any(i.isdigit() for i in inputString[-4:])):
        return inputString[:-4]

    else:
        return inputString
