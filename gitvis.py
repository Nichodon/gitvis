from Tkinter import *
from zlib import *
from os import listdir
from os.path import isfile, join
from pprint import pprint

'''

Todo:::

Everything visual is borken
Parsing pack

'''


graph = {}


class Node:
    def __init__(self, pos, ends, data):
        self.pos = pos
        self.ends = ends
        self.data = data.rstrip()


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


def mark(event):
    event.widget.scan_mark(event.x, event.y)


def dragto(event):
    event.widget.scan_dragto(event.x, event.y, gain=1)


def draw_node(canvas, node):
    pos = node.pos
    ends = node.ends
    data = node.data
    canvas.create_oval(pos[0] - 30, pos[1] - 25, pos[0] + 30, pos[1] + 25)
    canvas.create_text(pos[0], pos[1], text=data[:7])
    for point in ends:
        canvas.create_line(pos[0] - 30, pos[1], pos[0] - 30, pos[1] + point[1])
        canvas.create_line(pos[0] - 30, pos[1] + point[1],
                           pos[0] - 30 - point[0], pos[1] + point[1],
                           arrow=LAST)


def has_parent(node):
    data = node.parents[0]
    with open('.git/objects/' + data[:2] + '/' + data[2:]) as i:
        return 'parent' in decompress(i.read())

branch_names = [f for f in listdir('.git/refs/heads') if
                isfile(join('.git/refs/heads', f))]

branch_tips = []


for branch_name in branch_names:

    with open('.git/refs/heads/' + branch_name) as x:
        first_node = x.read()

    sha1_par = first_node.rstrip()
    branch_tips.append(sha1_par)

    while True:
        with open('.git/objects/' + sha1_par[:2] + '/' +
                  sha1_par[2:].rstrip()) as x:
            commit_body = x.read()
        commit_body = decompress(commit_body)
        lines = commit_body.split('\x00')
        parents_par = list(filter(lambda l: l.startswith('parent '),
                                  lines[1].split('\n')))
        parents_par = map(lambda l: l[len('parent '):], parents_par)
        graph[sha1_par] = parents_par
        if len(lines[1].split('parent ')) == 1:
            break
        sha1_par = lines[1].split('parent ')[1].split('\n')[0]

#pprint(graph)
allpaths = find_all_paths(graph, '8cc0f8e96ac33c63684fc82f2df338b9c8b367ee\n',
                         '4d1d35dcfc07a34c34efde4b87e2b50bf4d1a9c4')
root = graph.keys()[graph.values().index([])]

allpaths.sort(key=lambda e: -len(e))
#pprint(allpaths)

#pprint(branch_tips)

the_paths = []
for tip in branch_tips:
    the_paths.extend(find_all_paths(graph, tip, root))

the_paths.sort(key=lambda e: -len(e))
the_paths[0]

tk = Tk()

tk.minsize(width=750, height=500)
tk.maxsize(width=750, height=500)

lf1 = LabelFrame(tk, text='Tree', relief=SOLID, border=1)
lf1.grid(row=0, column=0)

width = len(the_paths[0])

c1 = Canvas(lf1, width=500, height=400, highlightthickness=0,
            scrollregion=(0, 0, width * 100 + 100, 400))

sc1 = Scrollbar(lf1, orient=HORIZONTAL)
sc1.grid(row=1, column=0, sticky='we')
sc1.config(command=c1.xview)

sc2 = Scrollbar(lf1, orient=VERTICAL)
sc2.grid(row=0, column=1, sticky='ns')
sc2.config(command=c1.yview)

c1.config(xscrollcommand=sc1.set, yscrollcommand=sc2.set)
c1.grid(row=0, column=0)
c1.bind('<ButtonPress-1>', mark)
c1.bind('<B1-Motion>', dragto)

lf2 = LabelFrame(tk, text='Information', relief=SOLID, border=1)
lf2.grid(row=0, column=1)

l1 = Label(lf2, text='[' + branch_name + ']: ' + first_node[:7])
l1.grid(row=0, column=0)

tk.wm_title('GitVis')

n = width * 100 + 100
for sha1 in the_paths[0][0:-1]:
    n -= 100
    node = Node([n, 100], [[40, 0]], sha1)
    draw_node(c1, node)
n -= 100
node = Node([n, 100], [], the_paths[0][-1])
draw_node(c1, node)

mainloop()
