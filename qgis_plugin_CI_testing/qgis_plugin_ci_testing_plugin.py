#!/usr/bin/env python
"""
/***************************************************************************

 QGIS Plugin CI Testing
 Copyright (C) 2019 Denis Rouzaud

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

DEBUG = False

import os

from PyQt5.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from qgis.gui import QgisInterface


class QgisPluginCiTesting:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

        # initialize translation
        qgis_locale = QLocale(QSettings().value("locale/userLocale"))
        locale_path = os.path.join(os.path.dirname(__file__), "i18n")
        self.translator = QTranslator()
        self.translator.load(qgis_locale, "swiss_locator", "_", locale_path)
        QCoreApplication.installTranslator(self.translator)

        self.trUtf8("some UTF-8 translation: un épilogue où l'on marche sur des œufs")

    def initGui(self):
        pass

    def unload(self):
        pass
