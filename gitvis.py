from Tkinter import *
from zlib import *
from os import listdir
from os.path import isfile, join
from pprint import pprint

'''

Todo:::

Parsing pack
Pack branch
Nonsense repo overlapping
Potential loopsg

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
    if start not in graph:
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
    data = node.data
    canvas.create_oval(pos[0] - 30, pos[1] - 25, pos[0] + 30, pos[1] + 25, fill='#ffffff')
    canvas.create_text(pos[0], pos[1], text=data[:7])


def draw_arrows(canvas, node):
    pos = node.pos
    ends = node.ends
    for point in ends:
        if point[1] == 0:
            canvas.create_line(pos[0] - 30, pos[1], pos[0] - 30 - point[0], pos[1], arrow=LAST)
        elif point[1] > 0:
            canvas.create_line(pos[0], pos[1] + 25, pos[0], pos[1] +
                               point[1])
            canvas.create_line(pos[0], pos[1] + point[1],
                               pos[0] - 30 - point[0], pos[1] + point[1],
                               arrow=LAST)
        else:
            canvas.create_line(pos[0] - 30, pos[1], pos[0] - point[0], pos[1])
            canvas.create_line(pos[0] - point[0], pos[1], pos[0] - point[0],
                               pos[1] + point[1]+25, arrow=LAST)


def has_parent(node):
    data = node.parents[0]
    with open('.git/objects/' + data[:2] + '/' + data[2:]) as i:
        return 'parent' in decompress(i.read())

branch_names = [f for f in listdir('.git/refs/heads') if
                isfile(join('.git/refs/heads', f))]

branch_tips = []
giant_commit_list = []

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
        commits_par = list(filter(lambda l: l.startswith('committer '),
                                  lines[1].split('\n')))
        commits_par = map(lambda l: l[len('committer '):], commits_par)[0].split(' ')[2:]
        commits_par[0] = int(commits_par[0])
        commits_par[0] += int(commits_par[1][:3]) * 3600 + int(commits_par[1][3:]) * 60
        commits_par.append(sha1_par)
        if commits_par not in giant_commit_list:
            giant_commit_list.append(commits_par)
        graph[sha1_par] = parents_par
        if len(lines[1].split('parent ')) == 1:
            break
        sha1_par = lines[1].split('parent ')[1].split('\n')[0]



giant_commit_list.sort(key=lambda y: y[0])
for i in range(len(giant_commit_list)):
    giant_commit_list[i].append((i + 1) * 100)
pprint(giant_commit_list)


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

tk = Tk()

tk.minsize(width=520, height=500)
tk.maxsize(width=520, height=500)

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

#lf2 = LabelFrame(tk, text='Information', relief=SOLID, border=1)
#lf2.grid(row=0, column=1)

#l1 = Label(lf2, text='[' + branch_name + ']: ' + first_node[:7])
#l1.grid(row=0, column=0)

tk.wm_title('GitVis')

positions = {}


x = {}
for gcl in giant_commit_list:
    x[gcl[2]] = gcl[3]

pprint(x)

for sha1 in the_paths[0][0:-1]:
    node = Node([x[sha1], 100], [[40, 0]], sha1)
    positions[sha1] = node
node = Node([100, 100], [], the_paths[0][-1])
positions[the_paths[0][-1]] = node

o = 100

for path in the_paths:
    started = False
    for i in range(len(path)):
        sha1 = path[i]
        if sha1 in positions:
            if started:
                other = positions[path[i - 1]]
                this = positions[sha1]
                other.ends.append([other.pos[0] - this.pos[0], -other.pos[1] + this.pos[1]])
            started = False
        else:
            if not started:
                o += 75
                positions[path[i - 1]].ends.append(
                    [40, o - positions[path[i - 1]].pos[1]])
            started = True
        if started:
            node = Node([x[sha1], o], [[40, 0]] if path[i + 1] not in positions else [], sha1)
            positions[sha1] = node

c1.config(scrollregion=(0, 0, width * 100 + 100, o + 100))

for position in positions:
    draw_arrows(c1, positions[position])

for position in positions:
    draw_node(c1, positions[position])

mainloop()
