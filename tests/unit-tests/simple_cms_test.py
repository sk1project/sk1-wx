
from uc2 import cms, uc2const

if __name__ == '__main__':
	lab = cms.do_simple_transform([0.0, 1.0, 0.0], uc2const.COLOR_RGB, uc2const.COLOR_LAB)
	rgb = cms.do_simple_transform(lab, uc2const.COLOR_LAB, uc2const.COLOR_RGB)
	print lab, rgb
