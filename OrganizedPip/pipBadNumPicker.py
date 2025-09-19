def badNumPicker(grid, groups, digitDict):
    for group in groups:
        match group['rule']:
            
            case 'sum':
                nums = [0, 1, 2, 3, 4, 5, 6]
                tileMinimum = group['rule_value'] - (6 * (len(group['tiles']) - 1))
                tileMaximum = group['rule_value']
                for tile in group['tiles']:
                    if tileMinimum > 0:
                        badMin = [x for x in nums if x<tileMinimum]
                        grid[tile[0]][tile[1]]['badNums'].append(badMin)
                    if tileMaximum < 6:
                        badMax = [x for x in nums if x>tileMaximum]
                        grid[tile[0]][tile[1]]['badNums'].append(badMax)

            case '=':
                badDigits = [digit for digit, count in digitDict.items() if count < len(group['tiles'])]
                for digits in badDigits:
                    for tile in group['tiles']:
                        grid[tile[0]][tile[1]]['badNums'].append(digits)


            
            case _:
                print("hello")
    
  