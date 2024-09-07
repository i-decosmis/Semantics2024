def fix_title(title):
    if ", The (" in title:
        name_film, _, year = title.rpartition(", The (")
        title = "The " + name_film + " (" + year
    return title


with open('movies.txt', 'r') as file:
    lines = file.readlines()


with open('movies.txt', 'w') as file:
    for line in lines:
        parts = line.split('::')
        parts[1] = fix_title(parts[1])
        new_line = '::'.join(parts)
        file.write(new_line)
        
