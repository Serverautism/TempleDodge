# if index is on collum with most rocks change it to collum with min rocks
if self.row_counter[x - 1] > min(self.row_counter) + self.max_collum_difference:
    self.available_rows.remove(x)
    self.blocked_rows.append([x, self.row_block_time])
    x = rows_min_index + 1
    print('x was max index')

    # check if index is blocked
    if x in self.available_rows:
        self.available_rows.remove(x)
        self.blocked_rows.append([x, self.row_block_time])
    else:
        x = random.choice(self.available_rows)
        print('prevented spawn in blocked row')