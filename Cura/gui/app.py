__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import sys
import os
import platform
import shutil
import glob
import warnings

try:
	#Only try to import the _core to save import time
	import wx._core
except ImportError:
	import wx


class CuraApp(wx.App):
	def __init__(self, files):
		if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
			from Cura.util import profile
			super(CuraApp, self).__init__(redirect=True, filename=os.path.join(profile.getBasePath(), 'output_log.txt'))
		else:
			super(CuraApp, self).__init__(redirect=False)

		self.mainWindow = None
		self.splash = None
		self.loadFiles = files

		self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

		if sys.platform.startswith('win'):
			#Check for an already running instance, if another instance is running load files in there
			from Cura.util import version
			from ctypes import windll
			import ctypes
			import socket
			import threading

			portNr = 0xCA00 + sum(map(ord, version.getVersion(False)))
			if len(files) > 0:
				try:
					other_hwnd = windll.user32.FindWindowA(None, ctypes.c_char_p('Cura - ' + version.getVersion()))
					if other_hwnd != 0:
						sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
						sock.sendto('\0'.join(files), ("127.0.0.1", portNr))

						windll.user32.SetForegroundWindow(other_hwnd)
						return
				except:
					pass

			socketListener = threading.Thread(target=self.Win32SocketListener, args=(portNr,))
			socketListener.daemon = True
			socketListener.start()

		if sys.platform.startswith('darwin'):
			#Do not show a splashscreen on OSX, as by Apple guidelines
			self.afterSplashCallback()
		else:
			from Cura.gui import splashScreen
			self.splash = splashScreen.splashScreen(self.afterSplashCallback)

	def MacOpenFile(self, path):
		try:
			self.mainWindow.OnDropFiles([path])
		except Exception as e:
			warnings.warn("File at {p} cannot be read: {e}".format(p=path, e=str(e)))

	def MacReopenApp(self, event):
		self.GetTopWindow().Raise()

	def MacHideApp(self, event):
		self.GetTopWindow().Show(False)

	def MacNewFile(self):
		pass

	def MacPrintFile(self, file_path):
		pass

	def OnActivate(self, e):
		if e.GetActive():
			self.GetTopWindow().Raise()
		e.Skip()

	def Win32SocketListener(self, port):
		import socket
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.bind(("127.0.0.1", port))
			while True:
				data, addr = sock.recvfrom(2048)
				try:
					wx.CallAfter(self.mainWindow.OnDropFiles, data.split('\0'))
				except Exception as e:
					warnings.warn("File at {p} cannot be read: {e}".format(p=data, e=str(e)))
		except:
			pass

	def afterSplashCallback(self):
		#These imports take most of the time and thus should be done after showing the splashscreen
		import webbrowser
		from Cura.gui import mainWindow
		from Cura.gui import configWizard
		from Cura.gui import newVersionDialog
		from Cura.util import profile
		from Cura.util import resources
		from Cura.util import version

		resources.setupLocalization(profile.getPreference('language'))  # it's important to set up localization at very beginning to install _

		#If we do not have preferences yet, try to load it from a previous Cura install
		if profile.getMachineSetting('machine_type') == 'unknown':
			try:
				otherCuraInstalls = profile.getAlternativeBasePaths()
				for path in otherCuraInstalls[::-1]:
					try:
						#print 'Loading old settings from %s' % (path)
						#profile.loadPreferences(os.path.join(path, 'preferences.ini'))
						#profile.loadProfile(os.path.join(path, 'current_profile.ini'))
						break
					except:
						import traceback
						print traceback.print_exc()
			except:
				import traceback
				print traceback.print_exc()

		#If we haven't run it before, run the configuration wizard.
		if profile.getMachineSetting('machine_type') == 'unknown':
			#Check if we need to copy our examples
			exampleFile = os.path.normpath(os.path.join(resources.resourceBasePath, 'example', '20mm_Calibration_Box.stl'))

			self.loadFiles = [exampleFile]
			if self.splash is not None:
				self.splash.Show(False)
			configWizard.ConfigWizard()
			i = 0
			profile.putMachineSetting('machine_name', 'M1', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 105.1, i)
			profile.putMachineSetting('machine_depth', 105.1, i)
			profile.putMachineSetting('machine_height', 105.1, i)
			profile.putMachineSetting('has_heated_bed', 'False', i)
			profile.putMachineSetting('extruder_head_size_min_x', '0', i)
			profile.putMachineSetting('extruder_head_size_min_y', '0', i)
			profile.putMachineSetting('extruder_head_size_max_x', '0', i)
			profile.putMachineSetting('extruder_head_size_max_y', '0', i)
			profile.putMachineSetting('extruder_head_size_height', '0', i)
			#profile.putProfileSetting('raft_base_linewidth', 2.0, i)
			profile.putProfileSetting('platform_adhesion', 'Raft', i)
			profile.putProfileSetting('travel_speed', 80, i)
			profile.putProfileSetting('fill_overlap', 4, i)
			i += 1
			profile.putMachineSetting('machine_name', 'M14', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 145.1, i)
			profile.putMachineSetting('machine_depth', 145.1, i)
			profile.putMachineSetting('machine_height', 146.1, i)
			profile.putMachineSetting('has_heated_bed', 'True', i)
			profile.putMachineSetting('extruder_head_size_min_x', '75', i)
			profile.putMachineSetting('extruder_head_size_min_y', '10', i)
			profile.putMachineSetting('extruder_head_size_max_x', '53', i)
			profile.putMachineSetting('extruder_head_size_max_y', '35', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('platform_adhesion', 'Raft', i)
			profile.putProfileSetting('travel_speed', 80, i)
			i += 1
			profile.putMachineSetting('machine_name', 'M15', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 145.1, i)
			profile.putMachineSetting('machine_depth', 145.1, i)
			profile.putMachineSetting('machine_height', 146.1, i)
			profile.putMachineSetting('has_heated_bed', 'True', i)
			profile.putMachineSetting('extruder_head_size_min_x', '75', i)
			profile.putMachineSetting('extruder_head_size_min_y', '10', i)
			profile.putMachineSetting('extruder_head_size_max_x', '53', i)
			profile.putMachineSetting('extruder_head_size_max_y', '35', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('platform_adhesion', 'Raft', i)
			profile.putProfileSetting('travel_speed', 80, i)
			i += 1
			profile.putMachineSetting('machine_name', 'M2030', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 205.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 306.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '77', i)
			profile.putMachineSetting('extruder_head_size_min_y', '13', i)
			profile.putMachineSetting('extruder_head_size_max_x', '53', i)
			profile.putMachineSetting('extruder_head_size_max_y', '35', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			i += 1
			profile.putMachineSetting('machine_name', 'M2048', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 205.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 486.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '77', i)
			profile.putMachineSetting('extruder_head_size_min_y', '13', i)
			profile.putMachineSetting('extruder_head_size_max_x', '53', i)
			profile.putMachineSetting('extruder_head_size_max_y', '35', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			i += 1
			profile.putMachineSetting('machine_name', 'K5/K6', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 205.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 306.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '30.10', i)
			profile.putMachineSetting('extruder_head_size_min_y', '27.80', i)
			profile.putMachineSetting('extruder_head_size_max_x', '36.90', i)
			profile.putMachineSetting('extruder_head_size_max_y', '62.60', i)
			profile.putMachineSetting('extruder_head_size_height', '42.80', i)
			profile.putProfileSetting('nozzle_type', 'V5', i)
			profile.putProfileSetting('fill_overlap', 2, i)
			profile.putProfileSetting('retraction_speed', 20.0, i)
			profile.putProfileSetting('retraction_amount', 1.0, i)
			profile.putProfileSetting('fill_overlap', 4, i)
			i += 1
			profile.putMachineSetting('machine_name', 'K300/M3145K/M3145', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 315.1, i)
			profile.putMachineSetting('machine_depth', 315.1, i)
			profile.putMachineSetting('machine_height', 456.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '15', i)
			profile.putMachineSetting('extruder_head_size_min_y', '15', i)
			profile.putMachineSetting('extruder_head_size_max_x', '48', i)
			profile.putMachineSetting('extruder_head_size_max_y', '36', i)
			profile.putMachineSetting('extruder_head_size_height', '57', i)
			profile.putProfileSetting('nozzle_type', 'V5', i)
			i += 1
			profile.putMachineSetting('machine_name', 'K400/M4141/M41S', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 415.1, i)
			profile.putMachineSetting('machine_depth', 415.1, i)
			profile.putMachineSetting('machine_height', 416.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '35', i)
			profile.putMachineSetting('extruder_head_size_min_y', '13', i)
			profile.putMachineSetting('extruder_head_size_max_x', '13', i)
			profile.putMachineSetting('extruder_head_size_max_y', '86', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			i += 1
			profile.putMachineSetting('machine_name', 'S300/M3145S', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 315.1, i)
			profile.putMachineSetting('machine_depth', 315.1, i)
			profile.putMachineSetting('machine_height', 456.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '22', i)
			profile.putMachineSetting('extruder_head_size_min_y', '18', i)
			profile.putMachineSetting('extruder_head_size_max_x', '30', i)
			profile.putMachineSetting('extruder_head_size_max_y', '76', i)
			profile.putMachineSetting('extruder_head_size_height', '58', i)
			profile.putProfileSetting('nozzle_type', 'V5', i)
			i += 1
			profile.putMachineSetting('machine_name', 'S400/S1', i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('extruder_amount', 1, i)
			profile.putMachineSetting('machine_width', 415.1, i)
			profile.putMachineSetting('machine_depth', 415.1, i)
			profile.putMachineSetting('machine_height', 416.1, i)
			profile.putMachineSetting('extruder_head_size_min_x', '35', i)
			profile.putMachineSetting('extruder_head_size_min_y', '13', i)
			profile.putMachineSetting('extruder_head_size_max_x', '13', i)
			profile.putMachineSetting('extruder_head_size_max_y', '86', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V5', i)
			i += 1
			profile.putMachineSetting('machine_name', _("X5/K5 MIX"), i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('machine_width', 190.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 306.1, i)
			profile.putMachineSetting('TIOON_type', _('Gradient'), i)
			profile.putProfileSetting('TIOON_enable', True, i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('retraction_speed', 20.0, i)
			profile.putProfileSetting('travel_speed', 100, i)
			profile.putProfileSetting('fill_overlap', 4, i)
			profile.putProfileSetting('is_Encrypt_Gcode', True, i)
			profile.putProfileSetting('wipe_tower_volume', 100, i)
			i += 1
			profile.putMachineSetting('machine_name', _('X5 Dual'), i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('machine_width', 190.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 306.1, i)
			profile.putMachineSetting('extruder_amount', 2, i)
			profile.putMachineSetting('extruder_head_size_min_x', '75', i)
			profile.putMachineSetting('extruder_head_size_min_y', '18', i)
			profile.putMachineSetting('extruder_head_size_max_x', '18', i)
			profile.putMachineSetting('extruder_head_size_max_y', '35', i)
			profile.putMachineSetting('extruder_head_size_height', '50', i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('travel_speed', 80, i)
			profile.putProfileSetting('overlap_dual', 0.15, i)
			profile.putProfileSetting('fill_overlap', 15, i)
			profile.putProfileSetting('retraction_dual_amount', 20.0, i)
			profile.putProfileSetting('retraction_speed', 20.0, i)
			profile.putProfileSetting('retraction_amount', 4.5, i)
			profile.putProfileSetting('solid_layer_thickness', 0.6, i)
			profile.putProfileSetting('print_temperature', 180, i)
			profile.putProfileSetting('print_temperature2', 180, i)
			profile.putProfileSetting('wipe_tower', 'True', i)
			profile.putProfileSetting('wipe_tower_volume', 50, i)
			profile.putMachineSetting('extruder_offset_x1', 12, i)
			profile.putProfileSetting('platform_adhesion', 'Raft', i)
			profile.putProfileSetting('retraction_hop', 0.2, i)
			profile.putProfileSetting('is_Encrypt_Gcode', True, i)
			i += 1
			profile.putMachineSetting('machine_name', _("M2030X"), i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('machine_width', 190.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 306.1, i)
			profile.putMachineSetting('TIOON_type', _('Gradient'), i)
			profile.putMachineSetting('extruder_offset_x0', -19.0, i)
			profile.putProfileSetting('TIOON_enable', True, i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('retraction_speed', 20.0, i)
			profile.putProfileSetting('travel_speed', 100, i)
			profile.putProfileSetting('is_Encrypt_Gcode', True, i)
			profile.putProfileSetting('wipe_tower_volume', 100, i)
			i += 1
			profile.putMachineSetting('machine_name', _("M2048X"), i)
			profile.putMachineSetting('machine_type', 'MakerPi', i)
			profile.putMachineSetting('machine_width', 190.1, i)
			profile.putMachineSetting('machine_depth', 205.1, i)
			profile.putMachineSetting('machine_height', 486.1, i)
			profile.putMachineSetting('TIOON_type', _('Gradient'), i)
			profile.putMachineSetting('extruder_offset_x0', -19.0, i)
			profile.putProfileSetting('TIOON_enable', True, i)
			profile.putProfileSetting('nozzle_type', 'V4', i)
			profile.putProfileSetting('retraction_speed', 20.0, i)
			profile.putProfileSetting('travel_speed', 100, i)
			profile.putProfileSetting('is_Encrypt_Gcode', True, i)
			profile.putProfileSetting('wipe_tower_volume', 100, i)

		if profile.getPreference('check_for_updates') == 'True':
			newVersion = version.checkForNewerVersion()
			if newVersion is not None:
				if self.splash is not None:
					self.splash.Show(False)
				if wx.MessageBox(_("A new version of Cura is available, would you like to download?"), _("New version available"), wx.YES_NO | wx.ICON_INFORMATION) == wx.YES:
					webbrowser.open(newVersion)
					return
		if profile.getMachineSetting('machine_name') == '':
			return
		self.mainWindow = mainWindow.mainWindow()
		if self.splash is not None:
			try:
				self.splash.Show(False)
			except:
				pass
		self.SetTopWindow(self.mainWindow)
		self.mainWindow.Show()
		self.mainWindow.OnDropFiles(self.loadFiles)
		if profile.getPreference('last_run_version') != version.getVersion(False):
			profile.putPreference('last_run_version', version.getVersion(False))
			newVersionDialog.newVersionDialog().Show()

		setFullScreenCapable(self.mainWindow)

		if sys.platform.startswith('darwin'):
			wx.CallAfter(self.StupidMacOSWorkaround)

	def StupidMacOSWorkaround(self):
		"""
		On MacOS for some magical reason opening new frames does not work until you opened a new modal dialog and closed it.
		If we do this from software, then, as if by magic, the bug which prevents opening extra frames is gone.
		"""
		dlg = wx.Dialog(None)
		wx.PostEvent(dlg, wx.CommandEvent(wx.EVT_CLOSE.typeId))
		dlg.ShowModal()
		dlg.Destroy()

if platform.system() == "Darwin": #Mac magic. Dragons live here. THis sets full screen options.
	try:
		import ctypes, objc
		_objc = ctypes.PyDLL(objc._objc.__file__)

		# PyObject *PyObjCObject_New(id objc_object, int flags, int retain)
		_objc.PyObjCObject_New.restype = ctypes.py_object
		_objc.PyObjCObject_New.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

		def setFullScreenCapable(frame):
			frameobj = _objc.PyObjCObject_New(frame.GetHandle(), 0, 1)

			NSWindowCollectionBehaviorFullScreenPrimary = 1 << 7
			window = frameobj.window()
			newBehavior = window.collectionBehavior() | NSWindowCollectionBehaviorFullScreenPrimary
			window.setCollectionBehavior_(newBehavior)
	except:
		def setFullScreenCapable(frame):
			pass

else:
	def setFullScreenCapable(frame):
		pass
