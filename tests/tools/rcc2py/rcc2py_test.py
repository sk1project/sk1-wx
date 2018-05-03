# -*- coding: utf-8 -*-
import os
from photo_rc import get_resource

file=get_resource(True)

os.system('display '+file.name)