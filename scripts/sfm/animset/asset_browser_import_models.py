# Asset Browser - Import Models
# =====================
# MIT License
# 
# Copyright (c) 2023 KiwifruitDev
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PySide import QtCore, QtGui, shiboken
from vs import g_pDataModel as dm
import vs, sfmApp, sfm, sfmUtils, json, os, math

if globals().get("assetBrowser_globalModelStack") is None:
    QtGui.QMessageBox.critical(None, "Asset Browser: Error", "Asset Browser is not loaded.")
else:
    # Create temporary AssetBrowser_ModelImport() instance
    assetBrowser_modelImport = AssetBrowser_ModelImport()
    # Loop models
    assetBrowser_modelImportErrorString = assetBrowser_modelImport.loopModels()
    # Delete temporary AssetBrowser_ModelImport() instance
    del assetBrowser_modelImport
    # Show error message if there was an error
    if assetBrowser_modelImportErrorString != "":
        QtGui.QMessageBox.critical(None, "Asset Browser: Error", assetBrowser_modelImportErrorString)
    #else:
        # Show success message
        #QtGui.QMessageBox.information(None, "Asset Browser: Model Import", "Imported %d model(s)." % len(assetBrowser_globalModelStack))
    # Delete error string
    del assetBrowser_modelImportErrorString
