#/usr/bin/python2

import os
import sys
from Tkinter import *

def echo_msg(msg, newline=True, flush=True):
    if newline:
        msg += '\n'
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()

FONT='Ubuntu\ Regular 12'
PATH = os.path.abspath(os.path.dirname(__file__))
TPATH = os.path.join(PATH, 'items')
PYTHONPATH= os.path.abspath(os.path.join(PATH,'..','..','src'))
os.environ['PYTHONPATH'] = PYTHONPATH

class ListFrame(Frame):
    tests=[]

    def __init__(self, master):
        Frame.__init__(self, master)
        self.list = Listbox(self, selectmode=EXTENDED)
        self.list.pack(fill=Y, anchor=W, side=LEFT)
        self.list.config(bd=0, font=FONT, relief=FLAT,
                         highlightthickness=1, highlightcolor='#aaaaaa',
                         highlightbackground='#aaaaaa',
                         selectborderwidth=0,
                         selectbackground='#388DE7', selectforeground='#ffffff')

        Frame(self, width=15).pack(anchor=W, side=LEFT)

        rframe = Frame(self)
        rframe.pack(fill=BOTH, expand=1, anchor=E, side=RIGHT)

        bframe = Frame(rframe)
        bframe.pack(fill=X, anchor=S, side=BOTTOM)

        self.exec_btn = Button(bframe, text='Execute', font=FONT, 
            command=self.execute)
        self.exec_btn.pack(side=RIGHT)

        Frame(bframe, width=5).pack(side=RIGHT)

        self.rescan_btn = Button(bframe, text='Rescan', font=FONT, 
            command=self.scan_tests)
        self.rescan_btn.pack(side=RIGHT)

        Frame(rframe, height=5).pack(fill=X, anchor=S, side=BOTTOM)


        self.text = Text(rframe, width = 45, font=FONT, bg=self['bg'],
                         highlightthickness=1, highlightcolor='#aaaaaa',
                         highlightbackground='#aaaaaa', borderwidth=0,)
        self.text.pack(fill=BOTH, expand=1, anchor=N, side=TOP)

        
        self.scan_tests()

        self.list.bind("<ButtonRelease-1>", self.on_select)
        self.list.bind("<Up>", self.on_up)
        self.list.bind("<Down>", self.on_down)
        self.list.bind("<Double-Button-1>", self.execute)
        self.list.bind('<Return>', self.execute)

    def on_up(self, *args):
        selection = self.list.curselection()[0] - 1
        if selection < 0 :
            selection = 0
        self.read_info(selection)

    def on_down(self, *args):
        selection = self.list.curselection()[0] + 1
        if selection == len(self.tests) :
            selection = len(self.tests) - 1
        self.read_info(selection)

    def on_select(self, *args):
        selection = self.list.curselection()[0]
        if selection < 0: 
            return
        self.read_info(selection)

    def execute(self, *args):
        selection = self.list.curselection()[0]
        if selection < 0: return
        fname = '{}.py'.format(self.tests[selection])
        fpath = os.path.join(TPATH, fname)
        if not os.path.isfile(fpath): return
        cmd = 'python %s' % fpath
        echo_msg('START %s' % fname, False)
        if not os.system(cmd):
            echo_msg('......[OK]')

    def scan_tests(self, *args):
        if self.tests:
            self.list.delete(0, END)
        self.tests = []
        file_items = os.listdir(TPATH)
        for fname in file_items:
            if os.path.isfile(os.path.join(TPATH, fname)) and fname.endswith('.py'):
                self.tests.append(fname.split('.py')[0])
        self.tests.sort()
        for item in self.tests:
            self.list.insert(END, item)
        self.exec_btn['state'] = 'disabled'
        self.text.configure(state='normal')
        self.text.delete(1.0, END)
        self.text.configure(state='disabled')
        if self.tests:
            self.list.selection_set(0)
            self.list.focus_set()
            self.read_info()

    def read_info(self, index=0):
        self.text.configure(state='normal')
        self.text.delete(1.0, END)
        fpath = os.path.join(TPATH, self.tests[index] + '.py')
        info = ''
        with open(fpath, 'rb') as fp:
            while True:
                line = fp.readline()
                if line.startswith('#'):
                    info += line[1:]
                else:
                    break
        self.text.insert(1.0, info)
        self.text.configure(state='disabled')
        self.exec_btn['state'] = 'normal'


root = Tk()
root.title('UI Tests')
frame = ListFrame(root)
frame.pack(fill=BOTH, expand=1, padx=15, pady=15)
root.geometry('{}x{}'.format(650, 450))
root.attributes('-zoomed', False)
root.mainloop()