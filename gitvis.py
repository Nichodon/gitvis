from Tkinter import *

with open('.git/HEAD') as x:
    f = x.read()

print f

f = f[5:].rstrip()

with open('.git/' + f) as x:
    g = x.read()

print g

tk = Tk()

tk.minsize(width=750, height=500)
tk.maxsize(width=750, height=500)

t = Message(tk, text='[' + f + ']: ' + g, width=500)
t.grid(row=0, column=0)

mainloop()
