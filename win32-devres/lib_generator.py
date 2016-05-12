import os

names = []

absdefpath = os.path.abspath('defs')

for item in os.listdir('defs'):
    item = str(item)
    names.append(item)
    
abslibpath = os.path.abspath('libs')

for item in names:
    defname = os.path.join(absdefpath, item)
    libname = os.path.join(abslibpath, item[:-4] + '.lib')
    os.system('LIB /NOLOGO /MACHINE:x86 /def:%s /out:%s' % (defname, libname))