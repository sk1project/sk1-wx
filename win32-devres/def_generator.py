import os

absnames = []

for item in os.listdir('dlls'):
    if not item == 'modules' or item[:4] == 'CORE':
        print item

