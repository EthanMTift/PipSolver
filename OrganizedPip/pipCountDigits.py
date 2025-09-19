

def countDigits(dominos):
    
    digitDict = {i: 0 for i in range(7)}

    # Count digits
    for a, b in dominos:
        if 0 <= a <= 6:
            digitDict[a] += 1
        if 0 <= b <= 6:
            digitDict[b] += 1
    
    return digitDict