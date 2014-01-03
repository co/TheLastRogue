import re


def get_library(file_name):
    lines = read_lines(file_name)
    return lines_to_library(lines)


def lines_to_library(lines):
    composite_library = {}
    for line in lines:
        if line_is_comment(line):
            continue
        elif line_is_composite_definition(line):
            last_composite = get_first_word_if_any(line)
            composite_library[last_composite] = {}
        elif not line.strip() == "":
            tokens = re.findall(r'".*"|[\w\-]+', line)
            stripped_tokens = [token.strip('" ') for token in tokens]
            composite_library[last_composite][stripped_tokens[0]] = stripped_tokens[1:]
    return composite_library


def read_lines(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    return lines


def get_first_word_if_any(line):
    words = line.split()
    if len(words) > 0:
        return words[0]
    else:
        return None


def line_is_composite_definition(line):
    if len(line) > 0:
        return line[0].isalpha()
    return False


def line_is_comment(line):
    striped_line = line.strip()
    if len(striped_line) > 0:
        return line.strip()[0] == "#"
    return False


    #Slime
    #    add monster_template
    #    add slime_template
    #    Name slime
    #    Health 30-45
    #    Strength 2
    #    Armor 3
    #    Awareness 5
    #    Icon SLIME
    #    Color GREEN
    #
    #    CanShareTileEntityMover