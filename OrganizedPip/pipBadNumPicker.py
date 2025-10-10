
def badNumPicker(grid, groups, digitDict):
    nums = [0, 1, 2, 3, 4, 5, 6]
    for group in groups:
        match group['rule']:
            # Fill every tile but one with 6 to find the smallest theoretical value
            # For largest theoretical value, just look at the 'rule_value' field
            case 'sum':
                nums = [0, 1, 2, 3, 4, 5, 6]
                tileMinimum = group['rule_value'] - (6 * (len(group['tiles']) - 1))
                tileMaximum = group['rule_value']
                for tile in group['tiles']:
                    if tileMinimum > 0:
                        badMin = [x for x in nums if x<tileMinimum]
                        if len(badMin) > 1:
                            grid[tile[0]][tile[1]]['badNums'].extend(badMin)
                        else:
                            grid[tile[0]][tile[1]]['badNums'].append(badMin[0])
                    if tileMaximum < 6:
                        badMax = [x for x in nums if x>tileMaximum]
                        if len(badMax) > 1:
                            grid[tile[0]][tile[1]]['badNums'].extend(badMax)
                        else:
                            grid[tile[0]][tile[1]]['badNums'].append(badMax[0])
            
            case '>sum':
                tileMinimum = ((group['rule_value'] + 1) - (6 * (len(group['tiles']) - 1)))
                for tile in group['tiles']:
                    if tileMinimum > 0:
                        badMin = [x for x in nums if x<tileMinimum]
                        if len(badMin) > 1:
                            grid[tile[0]][tile[1]]['badNums'].extend(badMin)
                        else:
                            grid[tile[0]][tile[1]]['badNums'].append(badMin[0])

            
            case '<sum':
                tileMaximum = group['rule_value'] - 1
                for tile in group['tiles']:
                    if tileMaximum < 6:
                        badMax = [x for x in nums if x>tileMaximum]
                        if len(badMax) > 1:
                            grid[tile[0]][tile[1]]['badNums'].extend(badMax)
                        else:
                            grid[tile[0]][tile[1]]['badNums'].append(badMax[0])
            
            
            # Look at how many spaces are in each = group, and discount numbers which occur in the dominos less than that amount of spaces

            case '=':
                badDigits = [digit for digit, count in digitDict.items() if count < len(group['tiles'])]
                for digits in badDigits:
                    for tile in group['tiles']:
                        grid[tile[0]][tile[1]]['badNums'].append(digits)


            
            case _:
                print("hello")
    
  