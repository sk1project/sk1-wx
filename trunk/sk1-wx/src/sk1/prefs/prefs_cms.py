# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, shutil

import wal

from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_LAB, \
COLOR_GRAY, COLOR_DISPLAY, ICC, ICM, INTENTS
from uc2.cms import get_profile_name, get_profile_descr


from sk1 import _, config, dialogs
from sk1.resources import icons, get_bmp

from generic import PrefPanel

COLORSPACES = [COLOR_RGB, COLOR_CMYK, COLOR_LAB, COLOR_GRAY, COLOR_DISPLAY]

class CMSPrefs(PrefPanel):

	pid = 'CMS'
	name = _('Color management')
	title = _('Color management and color profiles')
	icon_id = icons.PD_PREFS_CMS
	tabs = []

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):
		self.nb = wal.Notebook(self)

		#========Color management options
		self.page0 = CMS_Options(self.nb, self)
		self.page1 = CMS_Profiles(self.nb, self)
		self.page2 = CMS_Settings(self.nb, self)

		for item in [self.page0, self.page1, self.page2]:
			self.nb.add_page(item, item.name)

		self.pack(self.nb, expand=True, fill=True)
		self.built = True
		self.page0.activate_cms()

	def apply_changes(self):
		for item in self.nb.childs:
			item.apply_changes()

	def restore_defaults(self):
		for item in self.nb.childs:
			item.restore_defaults()

class CMS_Tab(wal.VPanel):

	name = ''
	prefpanel = None

	def __init__(self, parent, prefpanel):
		self.prefpanel = prefpanel
		wal.VPanel.__init__(self, parent)

	def apply_changes(self):pass
	def restore_defaults(self):pass


class CMS_Options(CMS_Tab):

	name = _('Color management')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)
		txt = _('Activate Color Management')
		self.cms_check = wal.Checkbox(self, txt, config.cms_use,
									onclick=self.activate_cms)

		self.pack(self.cms_check, align_center=False, padding_all=3)

		self.banner = wal.VPanel(self)
		self.banner.set_bg(wal.DARK_GRAY)
		bmp = get_bmp(self.banner, icons.PD_PREFS_CMS_BANNER)
		self.banner.pack(bmp, padding=2)
		self.pack(self.banner, expand=True, fill=True)
		txt = _('Note: If Color Management is not activated all colors '
			'will be processed using simple calculation procedures. Therefore '
			'resulted color values will be not accurate.')
		label = wal.Label(self, txt, fontsize=-3)
		label.set_enable(False)
		self.pack(label, fill=True, padding_all=5)

	def activate_cms(self):
		self.banner.set_visible(self.cms_check.get_value())
		nb = self.prefpanel.nb
		if self.cms_check.get_value() and len(nb.childs) < 2:
			nb.add_page(self.prefpanel.page1, self.prefpanel.page1.name)
			nb.add_page(self.prefpanel.page2, self.prefpanel.page2.name)
		elif not self.cms_check.get_value() and len(nb.childs) > 1:
			nb.remove_page(self.prefpanel.page1)
			nb.remove_page(self.prefpanel.page2)

	def apply_changes(self):
		config.cms_use = self.cms_check.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.cms_check.set_value(defaults['cms_use'])


class CMS_Profiles(CMS_Tab):

	name = _('Color profiles')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)

		txt = _('Colorspace profiles')
		self.pack(wal.Label(self, txt, fontbold=True), padding=2)
		self.pack(wal.HLine(self), fill=True, padding_all=2)

		grid = wal.GridPanel(self, cols=3, hgap=5, vgap=5)
		grid.add_growable_col(1)

		self.cs_widgets = {}
		self.cs_profiles = {}
		self.cs_config_profiles = {}

		self.cs_config = {COLOR_RGB:config.cms_rgb_profile,
					COLOR_CMYK:config.cms_cmyk_profile,
					COLOR_LAB:config.cms_lab_profile,
					COLOR_GRAY:config.cms_gray_profile,
					COLOR_DISPLAY:config.cms_display_profile}

		for colorspace in COLORSPACES[:-1]:
			txt = _('%s profile:') % colorspace
			grid.pack(wal.Label(grid, txt))
			combo = wal.Combolist(grid, items=[])
			self.cs_widgets[colorspace] = combo
			grid.pack(combo, fill=True)
			self.update_combo(colorspace)
			grid.pack(ManageButton(grid, self, colorspace))

		self.pack(grid, fill=True, padding_all=5)

		txt = _('Hardware profiles')
		self.pack(wal.Label(self, txt, fontbold=True), padding=2)
		self.pack(wal.HLine(self), fill=True, padding_all=2)

		grid = wal.GridPanel(self, cols=3, hgap=5, vgap=5)
		grid.add_growable_col(1)

		txt = _('Display profile:')
		grid.pack(wal.Label(grid, txt))
		combo = wal.Combolist(grid, items=[])
		self.cs_widgets[COLOR_DISPLAY] = combo
		grid.pack(combo, fill=True)
		self.update_combo(COLOR_DISPLAY)
		grid.pack(ManageButton(grid, self, COLOR_DISPLAY))

		self.pack(grid, fill=True, padding_all=5)

		txt = _('Use display profile')
		self.display_check = wal.Checkbox(self, txt,
									config.cms_use_display_profile,
									onclick=self.activate_display)
		self.pack(self.display_check, align_center=False)

		txt = _('Note: Display profile affects on '
				'document screen representation only. The profile for your '
				'hardware you can get either from monitor manufacture or '
				'calibrating monitor (preferred option) or download '
				'from ICC Profile Taxi service: ')
		label = wal.Label(self, txt, fontsize=-3)
		label.set_enable(False)
		self.pack(label, fill=True, padding_all=5)
		self.pack(wal.HtmlLabel(self, 'http://icc.opensuse.org/'))
		self.activate_display()

	def activate_display(self):
		combo = self.cs_widgets[COLOR_DISPLAY]
		combo.set_enable(self.display_check.get_value())

	def update_config_data(self, colorspace):
		if colorspace == COLOR_RGB:
			self.cs_config_profiles[colorspace] = config.cms_rgb_profiles.copy()
		elif colorspace == COLOR_CMYK:
			self.cs_config_profiles[colorspace] = config.cms_cmyk_profiles.copy()
		elif colorspace == COLOR_LAB:
			self.cs_config_profiles[colorspace] = config.cms_lab_profiles.copy()
		elif colorspace == COLOR_GRAY:
			self.cs_config_profiles[colorspace] = config.cms_gray_profiles.copy()
		else:
			self.cs_config_profiles[colorspace] = config.cms_display_profiles.copy()
		self.cs_profiles[colorspace] = self.get_profile_names(colorspace)

	def update_combo(self, colorspace, set_active=True):
		self.update_config_data(colorspace)
		combo = self.cs_widgets[colorspace]
		combo.set_items(self.cs_profiles[colorspace])
		if not set_active: return
		self.set_active_profile(combo, self.cs_config[colorspace], colorspace)

	def set_active_profile(self, widget, name, colorspace):
		profiles = self.get_profile_names(colorspace)
		if not name:
			widget.set_active(0)
		elif not name in profiles:
			widget.set_active(0)
			if colorspace == COLOR_RGB:
				config.cms_rgb_profile = ''
			elif colorspace == COLOR_CMYK:
				config.cms_cmyk_profile = ''
			elif colorspace == COLOR_LAB:
				config.cms_lab_profile = ''
			elif colorspace == COLOR_GRAY:
				config.cms_gray_profile = ''
			else:
				config.cms_display_profile = ''
		else:
			widget.set_active(profiles.index(name))

	def get_profile_names(self, colorspace):
		names = []
		default = _('Built-in %s profile') % (colorspace)
		names.append(default)
		names += self.cs_config_profiles[colorspace].keys()
		return names

	def apply_changes(self):
		for colorspace in COLORSPACES:
			profiles = self.get_profile_names(colorspace)
			combo = self.cs_widgets[colorspace]
			index = combo.get_active()
			profile_name = ''
			if index: profile_name = profiles[index]
			if colorspace == COLOR_RGB:
				config.cms_rgb_profile = profile_name
			elif colorspace == COLOR_CMYK:
				config.cms_cmyk_profile = profile_name
			elif colorspace == COLOR_LAB:
				config.cms_lab_profile = profile_name
			elif colorspace == COLOR_GRAY:
				config.cms_gray_profile = profile_name
			else:
				config.cms_display_profile = profile_name
		config.cms_use_display_profile = self.display_check.get_value()

	def restore_defaults(self):
		for item in COLORSPACES:
			self.cs_config[item] = ''
			self.update_combo(item)
		defaults = config.get_defaults()
		self.display_check.set_value(defaults['cms_use_display_profile'])

class ManageButton(wal.ImageButton):

	colorspace = ''
	owner = None

	def __init__(self, parent, owner, colorspace):
		self.owner = owner
		self.colorspace = colorspace
		txt = _('Add/remove %s profiles') % (colorspace)
		wal.ImageButton.__init__(self, parent, icons.PD_EDIT, tooltip=txt,
							flat=False, onclick=self.action)

	def action(self):
		app = self.owner.prefpanel.app
		dlg = self.owner.prefpanel.dlg
		ProfileManager(app, dlg, self.colorspace).show()
		combo = self.owner.cs_widgets[self.colorspace]
		profiles = self.owner.cs_profiles[self.colorspace]
		selected = profiles[combo.get_active()]
		self.owner.update_combo(self.colorspace)
		profiles = self.owner.cs_profiles[self.colorspace]
		if selected in profiles:
			combo.set_active(profiles.index(selected))


class ProfileManager(wal.CloseDialog):

	profiles = {}
	pf_list = []

	def __init__(self, app, parent, colorspace):
		self.app = app
		self.colorspace = colorspace
		size = (400, 250)
		title = _('%s profiles') % colorspace
		wal.CloseDialog.__init__(self, parent, title, size, wal.HORIZONTAL)

	def set_profiles(self):
		if self.colorspace == COLOR_RGB:
			self.profiles = config.cms_rgb_profiles.copy()
		elif self.colorspace == COLOR_CMYK:
			self.profiles = config.cms_cmyk_profiles.copy()
		elif self.colorspace == COLOR_LAB:
			self.profiles = config.cms_lab_profiles.copy()
		elif self.colorspace == COLOR_GRAY:
			self.profiles = config.cms_gray_profiles.copy()
		else:
			self.profiles = config.cms_display_profiles.copy()
		self.update_list()

	def save_profiles(self):
		if self.colorspace == COLOR_RGB:
			config.cms_rgb_profiles = self.profiles
		elif self.colorspace == COLOR_CMYK:
			config.cms_cmyk_profiles = self.profiles
		elif self.colorspace == COLOR_LAB:
			config.cms_lab_profiles = self.profiles
		elif self.colorspace == COLOR_GRAY:
			config.cms_gray_profiles = self.profiles
		else:
			config.cms_display_profiles = self.profiles
		self.update_list()

	def update_list(self):
		keys = self.profiles.keys()
		keys.sort()
		default = _('Built-in %s profile') % (self.colorspace)
		self.pf_list = [default, ] + keys

	def build(self):
		self.set_profiles()
		self.viewer = wal.SimpleList(self.panel, self.pf_list,
									on_select=self.selection_changed)
		self.panel.pack(self.viewer, expand=True, fill=True, padding_all=5)
		btn_box = wal.VPanel(self.panel)
		self.panel.pack(btn_box, fill=True, padding_all=5)

		self.import_btn = wal.Button(btn_box, _('Import'),
									onclick=self.import_profile)
		btn_box.pack(self.import_btn, fill=True, end_padding=5)
		self.remove_btn = wal.Button(btn_box, _('Remove'),
									onclick=self.remove_profile)
		btn_box.pack(self.remove_btn, fill=True, end_padding=5)
		self.info_btn = wal.Button(btn_box, _('Info'),
								onclick=self.profile_info)
		btn_box.pack(self.info_btn, fill=True, end_padding=5)
		self.viewer.set_active(0)

	def selection_changed(self, ret):
		index = self.viewer.get_active()
		self.remove_btn.set_enable(not index in (0, -1))
		self.info_btn.set_enable(not index in (0, -1))

	def import_profile(self):
		src = dialogs.get_open_file_name(self, self,
									config.profile_import_dir,
									_('Select profile to import'),
									file_types=[ICC, ICM])
		if not src: return
		name = get_profile_name(src)
		title = self.app.appdata.app_name
		if name is None:
			msg = _('Cannot open profile')
			msg = "%s '%s'" % (msg, src)
			sec = _('The profile may be corrupted or not supported format')
			wal.error_dialog(self, title, msg + '\n' + sec)
			return
		if name in self.pf_list:
			msg = _('Selected profile cannot be added to profile list:')
			msg = "%s '%s'" % (msg, name)
			sec = _('It seems you have imported this profile')
			wal.error_dialog(self, title, msg + '\n' + sec)
			return
		filename = os.path.basename(src)
		dst_dir = self.app.appdata.app_color_profile_dir
		dst = os.path.join(dst_dir, filename)
		if os.path.lexists(dst):
			msg = _('Selected file has been added to profile pool')
			msg = "%s '%s'" % (msg, src)
			sec = _('If you sure to import the file try renaming it')
			wal.error_dialog(self, title, msg + '\n' + sec)
			return
		try:
			shutil.copy(src, dst)
		except:
			msg = _('Cannot copy file')
			msg = "%s '%s'" % (msg, src)
			sec = _('Please check writing permissions for config directory:')
			sec += '\n%s' % dst_dir
			wal.error_dialog(self, title, msg + '\n' + sec)
			return
		config.profile_import_dir = os.path.dirname(src)
		self.profiles[name] = filename
		self.apply_changes()
		self.viewer.set_active(self.pf_list.index(name))

	def remove_profile(self):
		index = self.viewer.get_active()
		name = self.pf_list[index]
		filename = self.profiles[name]
		dst_dir = self.app.appdata.app_color_profile_dir
		dst = os.path.join(dst_dir, filename)
		if os.path.isfile(dst):
			os.remove(dst)
		self.profiles.pop(name)
		self.apply_changes()
		self.viewer.set_active(index - 1)

	def apply_changes(self):
		self.save_profiles()
		self.viewer.update(self.pf_list)

	def profile_info(self):
		index = self.viewer.get_active()
		name = self.pf_list[index]
		filename = self.profiles[name]
		dst_dir = self.app.appdata.app_color_profile_dir
		dst = os.path.join(dst_dir, filename)
		if os.path.isfile(dst): ProfileInfoViewer(self, dst).show()

class ProfileInfoViewer(wal.CloseDialog):

	def __init__(self, parent, filepath):
		self.filepath = filepath
		size = (400, 250)
		title = _('Profile info')
		wal.CloseDialog.__init__(self, parent, title, size, wal.HORIZONTAL)

	def build(self):
		name, copyrigth, info = get_profile_descr(self.filepath)
		filename = os.path.basename(self.filepath)
		if not copyrigth: copyrigth = '--'
		if not info:info = '--'
		grid = wal.GridPanel(self.panel, vgap=5, hgap=5)
		grid.add_growable_col(1)
		grid.add_growable_row(2)
		grid.add_growable_row(3)
		grid.pack(wal.Label(grid, _('Name:')))
		grid.pack(wal.Label(grid, name, True))
		grid.pack(wal.Label(grid, _('File:')))
		grid.pack(wal.Label(grid, filename))
		grid.pack(wal.Label(grid, _('Copyrigth:')))
		grid.pack(wal.Entry(grid, copyrigth, multiline=True, editable=False),
				fill=True)
		grid.pack(wal.Label(grid, _('Description:')))
		grid.pack(wal.Entry(grid, info, multiline=True, editable=False),
				fill=True)
		self.panel.pack(grid, fill=True, expand=True)


class CMS_Settings(CMS_Tab):

	name = _('Settings')

	def __init__(self, parent, prefpanel):
		CMS_Tab.__init__(self, parent, prefpanel)

		self.intents = INTENTS.keys()
		self.intents.sort()
		self.intents_names = []
		for item in self.intents:
			self.intents_names.append(INTENTS[item])

		panel = wal.VPanel(self.panel)

		#Intents panel
		int_panel = wal.LabeledPanel(panel, _('Rendering intents'))
		grid = wal.GridPanel(int_panel, vgap=5, hgap=5)

		grid.pack(wal.Label(grid, _('Display/RGB intent:')))
		self.display = wal.Combolist(grid, items=self.intents_names)
		self.display.set_active(self.intents.index(config.cms_rgb_intent))
		grid.pack(self.display)

		grid.pack(wal.Label(grid, _('Printer/CMYK intent:')))
		self.printer = wal.Combolist(grid, items=self.intents_names)
		self.printer.set_active(self.intents.index(config.cms_cmyk_intent))
		grid.pack(self.printer)

		int_panel.pack(grid, align_center=False, padding_all=10)
		panel.pack(int_panel, fill=True)

		#Simulate printer panel
		txt = _('Simulate printer on the screen')
		self.simulate_check = wal.Checkbox(panel, txt,
									config.cms_proofing,
									onclick=self.activate_simulation)

		sm_panel = wal.LabeledPanel(panel, widget=self.simulate_check)

		txt = _('Mark colors that are out of the printer gamut')
		self.outcolors_check = wal.Checkbox(sm_panel, txt,
									config.cms_gamutcheck,
									onclick=self.activate_outcolors)
		sm_panel.pack(self.outcolors_check, align_center=False, padding_all=5)

		clrpanel = wal.HPanel(sm_panel)
		clrpanel.pack((20, 1))
		self.alarm_label = wal.Label(clrpanel, _('Alarm color:'))
		clrpanel.pack(self.alarm_label, padding=5)
		self.color_btn = wal.ColorButton(clrpanel, config.cms_alarmcodes)
		clrpanel.pack(self.color_btn)
		sm_panel.pack(clrpanel, align_center=False, padding_all=2)

		txt = _('Separation for SPOT colors')
		self.separation_check = wal.Checkbox(sm_panel, txt,
									config.cms_proof_for_spot,
									onclick=self.activate_outcolors)
		sm_panel.pack(self.separation_check, align_center=False, padding_all=5)

		panel.pack(sm_panel, fill=True, padding=5)

		#Bottom checks
		txt = _('Use Blackpoint Compensation')
		self.bpc_check = wal.Checkbox(panel, txt,
									config.cms_bpc_flag)
		panel.pack(self.bpc_check, align_center=False)

		txt = _('Use Black preserving transforms')
		self.bpt_check = wal.Checkbox(panel, txt,
									config.cms_bpt_flag)
		panel.pack(self.bpt_check, align_center=False)

		self.panel.pack(panel, fill=True, padding_all=5)
		self.activate_simulation()

	def activate_simulation(self):
		self.outcolors_check.set_enable(self.simulate_check.get_value())
		self.separation_check.set_enable(self.simulate_check.get_value())
		self.activate_outcolors()

	def activate_outcolors(self):
		val = False
		if self.outcolors_check.get_enabled():
			val = self.outcolors_check.get_value()
		self.alarm_label.set_enable(val)
		self.color_btn.set_enable(val)

	def apply_changes(self):
		config.cms_rgb_intent = self.intents[self.display.get_active()]
		config.cms_cmyk_intent = self.intents[self.printer.get_active()]
		config.cms_proofing = self.simulate_check.get_value()
		config.cms_gamutcheck = self.outcolors_check.get_value()
		config.cms_proof_for_spot = self.separation_check.get_value()
		config.cms_alarmcodes = self.color_btn.get_value()
		config.cms_bpc_flag = self.bpc_check.get_value()
		config.cms_bpt_flag = self.bpt_check.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.display.set_active(self.intents.index(defaults['cms_rgb_intent']))
		self.printer.set_active(self.intents.index(defaults['cms_cmyk_intent']))
		self.simulate_check.set_value(defaults['cms_proofing'])
		self.outcolors_check.set_value(defaults['cms_gamutcheck'])
		self.separation_check.set_value(defaults['cms_proof_for_spot'])
		self.color_btn.set_value(defaults['cms_alarmcodes'])
		self.bpc_check.set_value(defaults['cms_bpc_flag'])
		self.bpt_check.set_value(defaults['cms_bpt_flag'])


