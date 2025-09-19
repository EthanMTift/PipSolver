def validate_groups(grid, groups):
    for group in groups:
        match group["rule"]:
            case 'sum':
                temp_sum = 0
                noneTiles = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        noneTiles += 1
                        continue
                    else:
                        temp_sum += int(grid[tile[0]][tile[1]]['value'])
                if int(group["rule_value"]) != temp_sum and noneTiles == 0:
                    return False
                else:
                    continue
            

            case '=':
                temp_equal_set = set()
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    temp_equal_set.add(grid[tile[0]][tile[1]]['value'])
                if len(temp_equal_set) > 1:
                    return False
                else:
                    continue


            case '!=':
                temp_equal_set = set()
                temp_none_count = 0
                for tile in group["tiles"]:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        temp_none_count += 1
                    else:    
                        temp_equal_set.add(grid[tile[0]][tile[1]]['value'])
                if (len(temp_equal_set) + temp_none_count) != len(group['tiles']):
                    return False
                else:
                    continue


            case 'constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] != group['rule_value']:
                        return False
                    else:
                        continue

            case '<constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] >= group['rule_value']:
                        return False
                    else:
                        continue

            case '>constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] <= group['rule_value']:
                        return False
                    else:
                        continue

            case '!constant':
                for tile in group['tiles']:
                    if grid[tile[0]][tile[1]]['value'] == None:
                        continue
                    if grid[tile[0]][tile[1]]['value'] == group['rule_value']:
                        return False
                    else:
                        continue

            case _:
                print("hi")
    return True