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

# TODO: This doesn't move to the camera like it should.

if assetBrowser_globalModelStack is None:
    QtGui.QMessageBox.critical(None, "Error", "Asset Browser is not loaded.")
    assetBrowser_globalModelStack = []

def QuaternionToEuler(x, y, z, w):
    ysqr = y * y
    t0 = -2.0 * (ysqr + z * z) + 1.0
    t1 = +2.0 * (x * y - w * z)
    t2 = -2.0 * (x * z + w * y)
    t3 = +2.0 * (y * z - w * x)
    t4 = -2.0 * (x * x + ysqr) + 1.0
    t2 = 1.0 if t2 > 1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    return [math.degrees(math.atan2(t3, t4)), math.degrees(math.asin(t2)), math.degrees(math.atan2(t1, t0))]

for modelName in assetBrowser_globalModelStack:
    # Get base name without extension and paths
    baseName = os.path.basename(modelName)
    baseName = os.path.splitext(baseName)[0]
    # Create model
    animSet = sfmUtils.CreateModelAnimationSet(baseName, modelName)
    # Position model at camera
    shot = sfm.GetCurrentShot()
    camera = shot.GetValue("camera")
    if camera is None:
        QtGui.QMessageBox.critical(None, "Error", "No camera found in current shot.")
    else:
        sfm.Select(animSet.GetName())
        cameraTransform = camera.GetValue("transform")
        cameraPos = cameraTransform.GetValue("position")
        cameraQuat = cameraTransform.GetValue("orientation")
        cameraAngles = QuaternionToEuler(cameraQuat.x, cameraQuat.y, cameraQuat.z, cameraQuat.w)
        sfm.Move( cameraPos.x, cameraPos.y, cameraPos.z )
        sfm.Rotate( cameraAngles[0], cameraAngles[1], cameraAngles[2] )
        

# Clear stack
assetBrowser_globalModelStack = []
