from Tkinter import *
from zlib import *


def mark(event):
    event.widget.scan_mark(event.x, event.y)


def dragto(event):
    event.widget.scan_dragto(event.x, event.y, gain=1)


def create_node(x_pos, y_pos, ends, data):
    c1.create_oval(x_pos - 30, y_pos - 25, x_pos + 30, y_pos + 25)
    c1.create_text(x_pos, y_pos, text=data)
    for point in ends:
        c1.create_line(x_pos - 30, y_pos, x_pos - 30, y_pos + point[1])
        c1.create_line(x_pos - 30, y_pos + point[1], x_pos - 30 - point[0],
                       y_pos + point[1], arrow=LAST)

with open('.git/HEAD') as x:
    f = x.read()

f = f[5:].rstrip()

with open('.git/' + f) as x:
    g = x.read()

tk = Tk()

tk.minsize(width=750, height=500)
tk.maxsize(width=750, height=500)

lf1 = LabelFrame(tk, text='Tree')
lf1.grid(row=0, column=0)

c1 = Canvas(lf1, width=500, height=400, highlightthickness=0,
            scrollregion=(0, 0, 600, 500))

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

lf2 = LabelFrame(tk, text='Information')
lf2.grid(row=0, column=1)

l1 = Label(lf2, text='[' + f + ']: ' + g[:7])
l1.grid(row=0, column=0)


create_node(500, 50, [[40, 0]], g[:7])
line = g

n = 400


while n >= 100:
    with open('.git/objects/' + line[:2] + '/' + line[2:].rstrip()) as x:
        h = x.read()

    h = decompress(h)

    lines = h.split('\x00')
    line = lines[1].split('parent ')[1].split('\n')[0]

    create_node(n, 50, [[40, 0]] if n > 100 else [], line[:7])
    n -= 100

mainloop()
