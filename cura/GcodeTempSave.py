# Copyright (c) 2017 Aleph Objects, Inc.
# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import os
import shutil
from threading import Thread

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class GcodeTempSave(Thread):

    def __init__(self, file_path_name=os.path.expanduser('~')+"\\temp.gcode"):
        super().__init__()
        self.file_path_name=file_path_name

    def run(self):
        save_gcode_file_path = os.path.expanduser('~') + "\\AppData\\local\\cura\\temp2.gcode"
        #Logger.log("w", "home_path a unknown type (%s) while parsing g-code.", f)
        shutil.copyfile(self.file_path_name, save_gcode_file_path)


