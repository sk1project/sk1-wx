import sys

if len(sys.argv) == 1:
	sys.argv += ['py2exe', ]

from distutils.core import setup
import py2exe


setup(
	options={'py2exe': {'bundle_files': 3,
						'compressed': True,
'includes':['base64', 'cgi', 'colorsys', 'copy', 'datetime', 'errno', 'inspect',
'math', 'new', 'numbers', 'os', 'platform', 'shutil', 'StringIO', 'cStringIO',
'struct', 'sys', 'tempfile', 'time', 'traceback', 'types',
'unicodedata', 'urllib2', 'webbrowser', 'xml.sax', 'zipfile', 'zlib', ],
						}},
	windows=[{'script': "src\\sk1.py",
			"icon_resources": [(1, "src\\sk1.ico")]
			}],
	)
