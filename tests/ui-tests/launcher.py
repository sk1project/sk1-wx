#/usr/in/python

import os
from Tkinter import *


PATH = os.path.abspath(os.path.dirname(__file__))
TPATH = os.path.join(PATH, 'items')
PYTHONPATH= os.path.abspath(os.path.join(PATH,'..','..','src'))
os.environ['PYTHONPATH'] = PYTHONPATH

class ListFrame(Frame):
    tests=[]

    def __init__(self, master):
        Frame.__init__(self, master)
        self.list = Listbox(self, selectmode=EXTENDED)
        self.list.pack(fill=BOTH, expand=1)
        self.list.config(bd=0, font='Ubuntu\ Regular 12', relief=FLAT,
                         highlightthickness=1, highlightcolor='#aaaaaa',
                         highlightbackground='#aaaaaa',
                         selectborderwidth=0,
                         selectbackground='#388DE7', selectforeground='#ffffff')

	self.scan_tests()
        for item in self.tests:
            self.list.insert(END, item)

        self.list.bind("<Double-Button-1>", self.on_select)
        self.list.bind('<Return>', self.on_select)

    def on_select(self, *args):
        selection = self.list.curselection()[0]
        if not selection: return
        fname = '{}.py'.format(self.tests[selection])
        fpath = os.path.join(TPATH, fname)
        if not os.path.isfile(fpath): return
        cmd = 'python %s' % fpath
        print 'START OF TEST %s' % fname
        os.system(cmd)
        print 'END OF TEST %s' % fname

    def scan_tests(self):
        self.tests = []
        file_items = os.listdir(TPATH)
        for fname in file_items:
            if os.path.isfile(os.path.join(TPATH, fname)) and fname.endswith('.py'):
                self.tests.append(fname.split('.py')[0])
        self.tests.sort()


root = Tk()
root.title('UI Tests')
frame = ListFrame(root)
frame.pack(fill=BOTH, expand=1, padx=15, pady=15)
root.geometry('{}x{}'.format(350, 450))
root.attributes('-zoomed', False)
root.mainloop()