from Tkinter import *
from zlib import *
from os import listdir
from os.path import isfile, join
from pprint import  pprint

'''

Todo:::

Duplicate commits

'''


graph = {}
nodes = []
branches = []


class Node:
    def __init__(self, pos, ends, data):
        self.pos = pos
        self.ends = ends
        self.data = data.rstrip()


class Commit:
    def __init__(self, sha1, parents):
        self.sha1 = sha1.rstrip()
        self.parents = parents

    def get_parents(self):
        if not self.parents:
            with open('.git/objects/' + self.sha1[:2] + '/' + self.sha1[2:]) \
                    as i:
                body = i.read()
            body = decompress(body)
            line_list = body.split('\x00')
            self.parents = list(filter(lambda l: l.startswith('parent '),
                                       line_list[1].split('\n')))
            self.parents = map(lambda l: l[len('parent '):], self.parents)
        return self.parents


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

with open('.git/HEAD') as x:
    head = x.read()

branch_names = [f for f in listdir('.git/refs/heads') if
                isfile(join('.git/refs/heads', f))]

for branch_name in branch_names:
    branch_commits = []

    with open('.git/refs/heads/' + branch_name) as x:
        first_node = x.read()

    sha1_par = first_node

    while True:
        with open('.git/objects/' + sha1_par[:2] + '/' +
                  sha1_par[2:].rstrip()) as x:
            commit_body = x.read()
        commit_body = decompress(commit_body)
        lines = commit_body.split('\x00')
        parents_par = list(filter(lambda l: l.startswith('parent '),
                                  lines[1].split('\n')))
        parents_par = map(lambda l: l[len('parent '):], parents_par)
        branch_commits.append(Commit(sha1_par, parents_par))
        graph[sha1_par] = parents_par
        if len(lines[1].split('parent ')) == 1:
            break
        sha1_par = lines[1].split('parent ')[1].split('\n')[0]

    branches.append(branch_commits)

pprint(graph)
allpaths = find_all_paths(graph, '8cc0f8e96ac33c63684fc82f2df338b9c8b367ee\n',
                         '4d1d35dcfc07a34c34efde4b87e2b50bf4d1a9c4')

allpaths.sort(key=lambda e: -len(e))
pprint(allpaths)

n = 50
for branch in branches:
    m = len(branch) * 100
    for commit in branch:
        nodes.append(Node([m, n], [[40, 0]] if m > 100 else [], commit.sha1))
        m -= 100
    n += 100

tk = Tk()

tk.minsize(width=750, height=500)
tk.maxsize(width=750, height=500)

lf1 = LabelFrame(tk, text='Tree', relief=SOLID, border=1)
lf1.grid(row=0, column=0)

width = 0
for branch in branches:
    width = max(width, len(branch))

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

for n in nodes:
    draw_node(c1, n)

tk.wm_title('GitVis')

mainloop()
