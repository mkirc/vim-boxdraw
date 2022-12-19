import sys
from math import log
from math import floor, ceil
from pprint import pprint

def get_diag_block(h, w, y1, x1, y2, x2):

    slope = (x2-x1) * (y2-y1)
     
    characters = [
        '|' if w < h else '-',
        # gotcha: y rises downwards (with line count)
        '/' if slope < 0 else '\\'   
    ]

    # get positions for both line and divider characters
    line_and_divider_positions = get_character_positions(w, h)

    diag_block = assemble_block(w, h, line_and_divider_positions, characters)
    
    if slope < 0:
        diag_block = mirror_on_x(diag_block)

    if h > w:
        return transpose(diag_block)
    else:
        return diag_block

def get_character_positions(w, h):

    # For steep slopes (ratios 1 < x < 2) we get smooth
    # diagonals by adding line characters to perfect divider
    # character sequences
    if max(w,h) / min(h,w) < 2 and max(w,h) / min(h,w) > 1:
        delta = max(w,h)-min(w,h)
        divider_positions, line_positions = place_dividers(max(w,h), delta)

    # We can build diagonals of infinite length for w/h ratios of 2
    # out of '-/'-atoms
    elif max(w,h) / min(w,h) == 2:
        line_positions = [i for i in range(max(w,h)) if i % 2 == 0]
        divider_positions =[j+1 for j in line_positions]

    # For shallow slopes (ratios x > 2) adding
    # divider characters to line characters yield smother diags
    else:
        # Here we tweak the output to perfect divider sequences
        # for w = h and to add bias towards terminal line characters else.
        # rationale: to get to height h we need (h-1) dividers
        n = h if w == h else (min(w,h)-1)
        line_positions, divider_positions = place_dividers(max(w,h), n)

    return line_positions, divider_positions

def assemble_block(w, h, ld_positions, characters):

    line_positions, divider_positions = ld_positions
    line_character, divider_character = characters

    diag_block = [[' ' for i in range(max(w,h))] for j in range(min(w,h))]
    current_line = 0

    for i in range(max(w,h)):

        if i in line_positions:
            diag_block[current_line][i] = line_character

        elif i in divider_positions:
            diag_block[current_line][i] = divider_character
            current_line += 1

    return diag_block


def mirror_on_x(block):

    return [block[j] for j in range(len(block)-1,-1,-1)]

def transpose(block):

    return [[block[j][i] for j in range(len(block))] for i in range(len(block[0]))]

def place_dividers(w, n):

    # to get an initial good guess we bisect the possible
    # range. this yields 2**depth <= n indices.
    divider_positions, rest = get_midpoints_for_sequence([i for i in range(w)], n)
    line_positions = [i for i in range(w) if i not in divider_positions]

    while rest > 0:
        # now we bisect the remaining indices until we
        # placed n dividers
        new_divider_positions, rest = get_midpoints_for_sequence(line_positions, rest)
        divider_positions += new_divider_positions
        line_positions = [i for i in range(w) if i not in divider_positions]

    return sorted(line_positions), sorted(divider_positions)

def get_midpoints_for_sequence(sequence, n_midpoints):

    depth = floor(log(n_midpoints, 2))
    tree = build_binary_tree(sequence, depth)

    midpoints = list(get_leave_values(tree, 'mid'))

    rest = n_midpoints - 2**depth

    return midpoints, rest

def build_binary_tree(sequence, max_depth, depth=0, root=None):

    if root is None:
        root = {
            'left' : None,
            'right' : None,
            'depth' : depth,
            'value' : sequence,
            'mid' : None
        }

    if len(sequence) == 1:
        root['mid'] = sequence[0]
        return root

    mid = len(sequence) // 2

    root['mid'] = sequence[mid]

    halves = ( sequence[:mid], sequence[mid:] )

    if depth+1 <= max_depth:

        root['left'] = build_binary_tree(halves[0], max_depth, depth+1)
        root['right'] = build_binary_tree(halves[1], max_depth, depth+1)

    return root

def get_leave_values(tree, key):

    if tree['left'] is not None:
        yield from get_leave_values(tree['left'], key)

    if (tree['left'] is None \
            and tree['right'] is None \
            and tree[key] is not None):
        yield tree[key]

    if tree['right'] is not None:
        yield from get_leave_values(tree['right'], key)


# if __name__ == '__main__':

#     h, w, y1, x1, y2, x2 = [int(arg) for arg in sys.argv[1:7]]

#     for line in get_diag_block(h, w, y1, x1, y2, x2)[::-1]:
#         print(''.join(line), len(line))

