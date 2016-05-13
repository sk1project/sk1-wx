import os

names = []

MSVCLIBS = ['mfc120u.dll',
'msvcp120.dll',
'msvcr90.dll',
'msvcr120.dll',
'vcomp120.dll', ]

abspath = os.path.abspath('dlls')

for item in os.listdir('dlls'):
	item = str(item)
	if not item[:4] == 'CORE' and not item in MSVCLIBS and not item == 'modules':
		names.append(item)

os.mkdir('defs')
absdefpath = os.path.abspath('defs')

for item in names:
	dllname = os.path.join(abspath, item)
	defname = os.path.join(absdefpath, item[:-4] + '.def')
	os.system('dumpbin /exports %s >%s' % (dllname, defname))
