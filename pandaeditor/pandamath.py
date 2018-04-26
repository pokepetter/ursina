
import operator



def distance(a, b):
    try:
        return a.getDistance(b)
    except:
        return (a.getXy() - b.getXy()).length()

def lerp(a, b, t):
    return a + (b - a) * t

def inverselerp(a, b, t) :
    return (a - b) / (t - b)

def clamp(value, floor, ceiling):
    return max(min(value, ceiling), floor)

def count_lines(file):
    all_lines = 0
    blank_lines = 0
    comment_lines = 0
    used_lines = 0

    with open(file) as f:
        for line in f:
            all_lines += 1

            if len(line.strip()) == 0:
                blank_lines += 1

            if line.strip().startswith('#'):
                comment_lines += 1
    print('all_lines:', all_lines)
    print('blank_lines:', blank_lines)
    print('comment_lines:', comment_lines)
    print('used_lines:', all_lines - blank_lines - comment_lines)
    return all_lines

def chunk_list(l, cunk_size):
    # yield successive chunks from list
    for i in range(0, len(l), cunk_size):
        yield l[i:i + cunk_size]

def size_list():
    #return a list of current python objects sorted by size
    globals_list = list()
    globals_list.clear()
    for e in globals():
        # object, size
        globals_list.append([e, sys.getsizeof(e)])
    globals_list.sort(key=operator.itemgetter(1), reverse=True)
    print('scene size:', globals_list)
