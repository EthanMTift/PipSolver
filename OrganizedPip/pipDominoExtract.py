def domino_extract(dominos):
    extracted = []
    for domino in dominos:
        extracted.append((int(domino['left_pips']), int(domino['right_pips'])))
    return extracted
