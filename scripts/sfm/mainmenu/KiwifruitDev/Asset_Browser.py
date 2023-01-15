# Asset Browser for SFM
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
import vs, sfmApp, sfm, sfmUtils, json, os, urllib, zipfile

assetBrowser_repo = "https://github.com/KiwifruitDev/SFM-Asset-Browser/releases/latest/download/assetbrowser.zip"
assetBrowser_modPath = "assetbrowser"
assetBrowser_globalModelStack = []
assetBrowser_version = "1"

class Tag:
    def __init__(self, tagName, tagValue, tagImage, children):
        self.tagName = tagName
        self.tagValue = tagValue
        self.tagImage = tagImage
        self.children = children
    tagName = "Favorites"
    tagValue = "favorites"
    tagImage = assetBrowser_modPath + "/images/assettags/favorites_sm.png"
    children = []

class Asset:
    def __init__(self, assetType, assetName, assetPath, children):
        self.assetType = assetType
        self.assetName = assetName
        self.assetPath = assetPath
        self.children = children
    assetType = "generic"
    assetName = ""
    assetPath = ""
    children = []

class AssetBrowserWindow(QtGui.QWidget):

    def __init__(self):
        super(AssetBrowserWindow, self).__init__()
        self.assetTree = {}
        self.assetIcons_Large = {}
        self.assetIcons_Small = {}
        self.MainWindow = sfmApp.GetMainWindow()
        # Set default icons
        self.assetIcons_Large["folder"] = assetBrowser_modPath + "/images/assettypes/folder_lg.png"
        self.assetIcons_Small["folder"] = assetBrowser_modPath + "/images/assettypes/folder_sm.png"
        self.assetIcons_Large["generic"] = assetBrowser_modPath + "/images/assettypes/generic_lg.png"
        self.assetIcons_Small["generic"] = assetBrowser_modPath + "/images/assettypes/generic_sm.png"
        self.assetIcons_Large["map"] = assetBrowser_modPath + "/images/assettypes/map_lg.png"
        self.assetIcons_Small["map"] = assetBrowser_modPath + "/images/assettypes/map_sm.png"
        self.assetIcons_Large["material"] = assetBrowser_modPath + "/images/assettypes/material_lg.png"
        self.assetIcons_Small["material"] = assetBrowser_modPath + "/images/assettypes/material_sm.png"
        self.assetIcons_Large["mesh"] = assetBrowser_modPath + "/images/assettypes/mesh_lg.png"
        self.assetIcons_Small["mesh"] = assetBrowser_modPath + "/images/assettypes/mesh_sm.png"
        self.assetIcons_Large["model"] = assetBrowser_modPath + "/images/assettypes/model_lg.png"
        self.assetIcons_Small["model"] = assetBrowser_modPath + "/images/assettypes/model_sm.png"
        self.assetIcons_Large["particles"] = assetBrowser_modPath + "/images/assettypes/particles_lg.png"
        self.assetIcons_Small["particles"] = assetBrowser_modPath + "/images/assettypes/particles_sm.png"
        self.assetIcons_Large["sky"] = assetBrowser_modPath + "/images/assettypes/sky_lg.png"
        self.assetIcons_Small["sky"] = assetBrowser_modPath + "/images/assettypes/sky_sm.png"
        self.assetIcons_Large["text"] = assetBrowser_modPath + "/images/assettypes/text_lg.png"
        self.assetIcons_Small["text"] = assetBrowser_modPath + "/images/assettypes/text_sm.png"
        self.assetIcons_Large["texture"] = assetBrowser_modPath + "/images/assettypes/texture_lg.png"
        self.assetIcons_Small["texture"] = assetBrowser_modPath + "/images/assettypes/texture_sm.png"
        self.assetIcons_Large["sound"] = assetBrowser_modPath + "/images/assettypes/sound_lg.png"
        self.assetIcons_Small["sound"] = assetBrowser_modPath + "/images/assettypes/sound_sm.png"
        self.assetIcons_Large["sfmsession"] = assetBrowser_modPath + "/images/assettypes/sfmsession_lg.png"
        self.assetIcons_Small["sfmsession"] = assetBrowser_modPath + "/images/assettypes/sfmsession_sm.png"
        # Init UI
        self.initUI()

    assetTypes = {
        ".bsp": "map",

        ".vmt": "material",

        ".vtf": "texture",

        ".mdl": "model",

        #".vtx": "mesh",
        #".phy": "mesh",
        #".vvd": "mesh",

        ".pcf": "particles",

        #".txt": "text",
        #".cfg": "text",
        #".py": "text",

        ".dmx": "sfmsession",

        ".wav": "sound",
        ".mp3": "sound",
    }

    forbiddenAssets = [
        "vscripts",
        "playerclasses",
        "renders",
        "presets",
        "graphs",
        "mapsrc",
        "soundcache",
        "midi",
    ]

    whiteList = [
        "maps",
        "models",
        "materials",
        "particles",
        "sound",
        "elements",
    ]

    rootAsset = Asset("folder", "Root", ".", [])
    
    tags = []

    defaultTags = [
        Tag("Favorites", "favorites", assetBrowser_modPath + "/images/assettags/favorites_sm.png", []),
        Tag("Red", "red", assetBrowser_modPath + "/images/assettags/red_sm.png", []),
        Tag("Green", "green", assetBrowser_modPath + "/images/assettags/green_sm.png", []),
        Tag("Blue", "blue", assetBrowser_modPath + "/images/assettags/blue_sm.png", []),
        Tag("Model Stack", "modelstack", assetBrowser_modPath + "/images/assettags/modelstack_sm.png", []),
    ]

    def getTypeOfAsset(self, assetFile, fullPath):
        # Check if assetFile is a folder
        if os.path.isdir(fullPath):
            return "folder"
        # Check if assetFile is inside of skybox folder
        if "skybox" in assetFile:
            return "sky"
        # Get file extension
        fileExtension = os.path.splitext(assetFile)[1]
        # Check if file extension is in assetTypes
        if fileExtension in self.assetTypes:
            return self.assetTypes[fileExtension]
        return "generic"

    def initUI(self):
        # Create inner widget (stores both grid and list)
        self.innerWidget = QtGui.QWidget()
        self.innerWidgetLayout = QtGui.QHBoxLayout()
        self.innerWidget.setLayout(self.innerWidgetLayout)
        self.innerWidgetLayout.setContentsMargins(0,0,0,0)
        self.innerWidgetLayout.setSpacing(0)
        self.innerWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create list on left side (allow resizing with splitter)
        self.listWidget = QtGui.QWidget()
        self.listWidgetLayout = QtGui.QVBoxLayout()
        self.listWidget.setLayout(self.listWidgetLayout)
        self.listWidget.setMinimumWidth(200)
        self.listWidget.setMaximumWidth(1000)
        self.listWidget.setMinimumHeight(400)
        self.listWidget.setMaximumHeight(1000)
        self.listWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.listWidgetLayout.setContentsMargins(0,0,0,0)
        self.listWidgetLayout.setSpacing(0)
        self.listWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create grid on right side (doesn't allow resizing, sticks to list)
        self.gridWidget = QtGui.QWidget()
        self.gridWidgetLayout = QtGui.QVBoxLayout()
        self.gridWidget.setLayout(self.gridWidgetLayout)
        self.gridWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.gridWidgetLayout.setContentsMargins(0,0,0,0)
        self.gridWidgetLayout.setSpacing(0)
        self.gridWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create list tree
        self.list = QtGui.QTreeWidget()
        self.list.setHeaderHidden(True)
        self.list.setIndentation(0)
        self.list.setRootIsDecorated(False)
        self.list.setUniformRowHeights(True)
        self.list.setSortingEnabled(False)
        self.list.setDragEnabled(False)
        self.list.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.list.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list.setIconSize(QtCore.QSize(16,16))
        self.list.itemClicked.connect(self.listItemClicked)
        self.list.customContextMenuRequested.connect(self.listContextMenu)
        self.listWidgetLayout.addWidget(self.list)
        # Create grid list (QListWidget with icons)
        self.gridList = QtGui.QListWidget()
        self.gridList.setViewMode(QtGui.QListView.IconMode)
        self.gridList.setResizeMode(QtGui.QListView.Adjust)
        self.gridList.setMovement(QtGui.QListView.Static)
        self.gridList.setSpacing(8)
        self.gridList.setFlow(QtGui.QListView.LeftToRight)
        self.gridList.setWrapping(True)
        self.gridList.setUniformItemSizes(True)
        self.gridList.setDragEnabled(False)
        self.gridList.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.gridList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.gridList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.gridList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gridList.setIconSize(QtCore.QSize(16, 16))
        self.gridList.setGridSize(QtCore.QSize(128, 128 + 32))
        self.gridList.itemClicked.connect(self.gridItemClicked)
        self.gridList.itemDoubleClicked.connect(self.gridItemDoubleClicked)
        self.gridList.customContextMenuRequested.connect(self.gridItemRightClicked)
        self.gridWidgetLayout.addWidget(self.gridList)
        # Create splitter between list and grid
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.listWidget)
        self.splitter.addWidget(self.gridWidget)
        self.splitter.setSizes([200, 400])
        # Add to inner widget
        self.innerWidgetLayout.addWidget(self.splitter)
        # Set self (outer) widget (stores inner widget and toolbar)
        self.outerWidgetLayout = QtGui.QVBoxLayout()
        self.setLayout(self.outerWidgetLayout)
        self.outerWidgetLayout.setContentsMargins(0,0,0,0)
        self.outerWidgetLayout.setSpacing(0)
        self.outerWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create toolbar
        self.toolbar = QtGui.QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        self.toolbar.setContentsMargins(0,0,0,0)
        self.toolbar.setOrientation(QtCore.Qt.Horizontal)
        self.toolbar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.toolbar.setStyleSheet("QToolBar { border: 0px; }")
        self.toolbarLayout = QtGui.QHBoxLayout()
        self.toolbarLayout.setContentsMargins(0,0,0,0)
        self.toolbarLayout.setSpacing(0)
        self.toolbarLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.toolbar.setLayout(self.toolbarLayout)
        # Create toolbar buttons
        # TODO: Add buttons to toolbar
        # Add toolbar to outer widget
        self.outerWidgetLayout.addWidget(self.toolbar)
        # Add inner widget to outer widget
        self.outerWidgetLayout.addWidget(self.innerWidget)
        # DEBUG: Add 10 controls to each list to test
        #for i in range(10):
        #    item = QtGui.QListWidgetItem()
        #    item.setText("Item %d" % i)
        #    item.setData(QtCore.Qt.DecorationRole, QtGui.QImage(self.assetIcons_Large["generic"]))
        #    self.gridList.addItem(item)
        #    item_small = QtGui.QTreeWidgetItem()
        #    item_small.setText(0, "Item %d" % i)
        #    item_small.setIcon(0, QtGui.QPixmap.fromImage(self.assetIcons_Small["generic"]))
        #    self.list.addTopLevelItem(item_small)
        # Make sure assetBrowser_modPath exists
        if not os.path.isdir(assetBrowser_modPath):
            os.makedirs(assetBrowser_modPath)
        #self.recursiveScan(".") # game root
        # Get folders in .
        for item in os.listdir("."):
            fullpath = os.path.join(".", item)
            if os.path.isdir(fullpath):
                self.recursiveScan(fullpath) # Add mod folder
        # Check version
        self.checkVersion()
        # Update tags
        self.loadAssetTags()
        # Update list for tags
        self.addTagsToList()
        # Update list
        self.recursiveUpdateList()
        # Expand top level items
        for i in range(self.list.topLevelItemCount()):
            self.list.topLevelItem(i).setExpanded(True)
        # Click on first item
        self.list.setCurrentItem(self.list.topLevelItem(0))
        self.listItemClicked(self.list.topLevelItem(0))

    def recursiveScan(self, path, parent=None):
        # Scan the given path recursively
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            assetType = self.getTypeOfAsset(item, fullpath)
            # Don't even parse generic assets
            if assetType == "generic":
                continue
            asset = Asset(assetType, item, fullpath, [])
            # Does asset already exist in parent?
            taken = False
            if parent:
                for child in parent.children:
                    if child.assetName == asset.assetName:
                        asset = child
                        taken = True
                        break
            else:
                for child in self.rootAsset.children:
                    if child.assetName == asset.assetName:
                        asset = child
                        taken = True
                        break
            # Does the path contain a whitelist entry?
            whitelistValid = False
            for whitelist in self.whiteList:
                if whitelist in fullpath:
                    whitelistValid = True
                    break
            if not whitelistValid:
                continue
            # Check if forbidden
            if asset.assetName in self.forbiddenAssets:
                continue
            # Only types allowed in root are folders
            if parent == None and assetType != "folder":
                continue
            # Add asset to parent
            if not taken:
                if parent:
                    parent.children.append(asset)
                else:
                    self.rootAsset.children.append(asset)
            # Check if asset is a folder
            if asset.assetType == "folder":
                # Scan folder
                self.recursiveScan(fullpath, asset)

    def recursiveUpdateList(self, assetParent=None, itemParent=None, depth=0):
        if assetParent == None:
            assetParent = self.rootAsset
        depthText = ""
        for i in range(depth):
            depthText += "- "
        # Don't add files
        if assetParent.assetType != "folder":
            return
        # Add asset to list
        item_small = QtGui.QTreeWidgetItem(itemParent)
        item_small.setText(0, depthText + assetParent.assetName)
        item_small.setIcon(0, QtGui.QPixmap.fromImage(QtGui.QImage(self.assetIcons_Small[assetParent.assetType])))
        item_small.setToolTip(0, assetParent.assetPath)
        # Add to list
        if itemParent:
            itemParent.addChild(item_small)
        else:
            self.list.addTopLevelItem(item_small)
        # Add children
        for child in assetParent.children:
            self.recursiveUpdateList(child, item_small, depth+1)
    
    def recursiveGetAssetFromPath(self, path, assetParent=None):
        if assetParent == None:
            assetParent = self.rootAsset
        if assetParent.assetPath == path:
            return assetParent
        else:
            for child in assetParent.children:
                asset = self.recursiveGetAssetFromPath(path, child)
                if asset:
                    return asset
        return None

    def assetClicked(self, asset):
        # Get base path (remove .\*\*\)
        basePath = asset.assetPath
        basePath = basePath[basePath.find("\\")+1:]
        basePath = basePath[basePath.find("\\")+1:]
        # Models use a prefix, others don't
        if(asset.assetType != "model"):
            basePath = basePath[basePath.find("\\")+1:]
        # Parse \ as /
        basePath = basePath.replace("\\", "/")
        # Parse each asset type
        if asset.assetType == "map":
            pass
        elif asset.assetType == "model":
            pass
        elif asset.assetType == "particle":
            pass
        elif asset.assetType == "sound":
            # Play sound
            sfm.console("play " + basePath)

    def assetDoubleClicked(self, asset):
        # Get base path (remove .\*\*\)
        basePath = asset.assetPath
        # TODO: What about text?
        # SFM sessions don't have a base path and materials/textures need cwd
        if asset.assetType != "sfmsession" and asset.assetType != "material" and asset.assetType != "texture":
            basePath = basePath[basePath.find("\\")+1:]
            basePath = basePath[basePath.find("\\")+1:]
            # Models use a prefix, others don't
            if asset.assetType != "model":
                basePath = basePath[basePath.find("\\")+1:]
                # Parse \ as /
                basePath = basePath.replace("\\", "/")
        else:
            # Remove .\ from path
            basePath = basePath[2:]
            # Add cwd to path
            basePath = os.path.join(os.getcwd(), basePath)
        # Parse each asset type
        if asset.assetType == "map":
            # Load map
            sfmApp.LoadMap(basePath)
            # Disable undo system
            dm.SetUndoEnabled(False)
            # Get current shot
            shot = sfmApp.GetShotAtCurrentTime(sfmApp.GetHeadTimeInFrames())
            # Set mapname in shot
            shot.SetValue("mapname", basePath)
            # Enable undo system
            dm.SetUndoEnabled(True)
        elif asset.assetType == "model":
            # Show information on how to import a model
            QtGui.QMessageBox.information(self, "Asset Browser: Model Import", "To import models, right click and check the \"Model Stack\" tag, then run\nthe \"asset_browser_import_models\" rig script from any animation set.")
        elif asset.assetType == "sfmsession":
            # Close current session and open new one
            sfmApp.CloseDocument(forceSilent=False)
            sfmApp.OpenDocument(basePath)
        elif asset.assetType == "material" or asset.assetType == "texture":
            # Open in external editor (vtfedit? vscode?)
            os.startfile(basePath)

    def listItemClicked(self, item):
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip(0))
        if asset:
            # Is it a folder?
            if asset.assetType != "folder":
                return
            # Reset grid icons and add new ones
            self.gridList.clear()
            # Add children
            for child in asset.children:
                # Don't add folders
                if child.assetType == "folder":
                    continue
                item = QtGui.QListWidgetItem()
                item.setText(child.assetName)
                item.setData(QtCore.Qt.DecorationRole, QtGui.QImage(self.assetIcons_Large[child.assetType]))
                item.setToolTip(child.assetPath)
                self.gridList.addItem(item)
        else:
            # Presume tag was clicked
            tagValue = item.toolTip(0)
            # Reset grid icons and add new ones
            self.gridList.clear()
            for tag in self.tags:
                if tag.tagValue == tagValue:
                    for asset in tag.children:
                        item = QtGui.QListWidgetItem()
                        item.setText(asset.assetName)
                        item.setData(QtCore.Qt.DecorationRole, QtGui.QImage(self.assetIcons_Large[asset.assetType]))
                        item.setToolTip(asset.assetPath)
                        self.gridList.addItem(item)
                    break
    
    def gridItemClicked(self, item):
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip())
        if asset:
            self.assetClicked(asset)

    def gridItemRightClicked(self):
        # Get item
        item = self.gridList.currentItem()
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip())
        # Create context menu
        menu = QtGui.QMenu()
        # Add actions text
        action = QtGui.QAction("Asset:", self)
        action.setEnabled(False)
        menu.addAction(action)
        # Add preview action
        #action = QtGui.QAction("Preview", self)
        #action.triggered.connect(lambda: self.assetClicked(asset))
        #menu.addAction(action)
        # Add import action
        #action = QtGui.QAction("Import", self)
        #action.triggered.connect(lambda: self.assetDoubleClicked(asset))
        #menu.addAction(action)
        # Add copy path action
        action = QtGui.QAction("Copy path", self)
        action.triggered.connect(lambda: self.copyPath(asset))
        menu.addAction(action)
        # Add open folder action
        action = QtGui.QAction("Open folder", self)
        action.triggered.connect(lambda: self.openFolder(asset))
        menu.addAction(action)
        # Add tag text
        action = QtGui.QAction("Tags:", self)
        action.setEnabled(False)
        menu.addAction(action)
        # Add tag actions
        for tag in self.tags:
            # Only add model stack if model
            if tag.tagValue == "modelstack" and asset.assetType != "model":
                continue
            action = QtGui.QAction(tag.tagName, self)
            action.setCheckable(True)
            for taggedAsset in tag.children:
                if taggedAsset.assetPath == asset.assetPath:
                    action.setChecked(True)
                    break
            action.triggered.connect(lambda tagValue=tag.tagValue: self.tagAsset(asset, tagValue))
            menu.addAction(action)
        # Show menu
        menu.exec_(QtGui.QCursor.pos())

    def copyPath(self, asset):
        # Remove .\ from path
        path = asset.assetPath[2:]
        # Add cwd to path
        path = os.path.join(os.getcwd(), path)
        # Copy path to clipboard
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(path)

    def openFolder(self, asset):
        # Get folder path
        folderPath = asset.assetPath
        folderPath = folderPath[0:folderPath.rfind("\\")]
        # Open folder
        os.startfile(folderPath)
    
    def tagAsset(self, asset, tagValue):
        tag = None
        # Get tag
        for selfTag in self.tags:
            if selfTag.tagValue == tagValue:
                tag = selfTag
                break
        # Check if asset is already tagged
        tagged = False
        for taggedAsset in tag.children:
            if taggedAsset.assetPath == asset.assetPath:
                # Remove tag
                tag.children.remove(taggedAsset)
                tagged = True
        if not tagged:
            # Add tag
            tag.children.append(asset)
        # If modelstack tag, add to model stack
        if tag.tagValue == "modelstack":
            # Get model name
            basePath = asset.assetPath
            basePath = basePath[basePath.find("\\")+1:]
            basePath = basePath[basePath.find("\\")+1:]
            baseName = basePath[basePath.rfind("/")+1:]
            # Add model to creation stack
            if tagged:
                # Remove model from stack
                assetBrowser_globalModelStack.remove(baseName)
            else:
                # Add model to stack
                assetBrowser_globalModelStack.append(baseName)
        # Save tags
        self.saveAssetTags()
        # Reload list
        self.list.setCurrentItem(self.list.currentItem())
        self.listItemClicked(self.list.currentItem())
    
    def gridItemDoubleClicked(self, item):
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip())
        self.assetDoubleClicked(asset)
        
    # Load asset tags from json file
    def loadAssetTags(self):
        # Format: {"tags":[{"tagName": "Tag Name", "tagValue": "tagValue", "tagImage": assetBrowser_modPath + "/images/assettags/tag_sm.png", "children": ["./hl2/sound/error.wav"]}, ...]}
        # Open file if it exists
        if not os.path.isfile(assetBrowser_modPath + "/assetTags.json"):
            # Create file
            f = open(assetBrowser_modPath + "/assetTags.json", "w")
            # Create json from defaultTags
            preJson = {}
            preJson["tags"] = []
            for tag in self.defaultTags:
                tagObject = {}
                tagObject["tagName"] = tag.tagName
                tagObject["tagValue"] = tag.tagValue
                tagObject["tagImage"] = tag.tagImage
                tagObject["children"] = []
                for child in tag.children:
                    tagObject["children"].append(child.assetPath)
                preJson["tags"].append(tagObject)
            # Write json to file
            try:
                json.dump(preJson, f)
                f.close()
            except:
                if f:
                    f.close()
                QtGui.QMessageBox.critical(self, "Asset Browser: Error", "Error writing to assetTags.json. Asset tags will not be available.\nMaybe try restarting Source Filmmaker? Delete assetTags.json if possible.")
        try:
            f = open(assetBrowser_modPath + "/assetTags.json", "r")
            # Parse json
            data = json.load(f)
            # Close file
            f.close()
            # Add tag to "tags" list
            for tag in data["tags"]:
                # Get assets from children
                assets = []
                for child in tag["children"]:
                    # Replace / with \
                    child = child.replace("/", "\\")
                    asset = self.recursiveGetAssetFromPath(child)
                    if asset:
                        assets.append(asset)
                # Add tag
                self.tags.append(Tag(tag["tagName"], tag["tagValue"], tag["tagImage"], assets))
        except:
            QtGui.QMessageBox.critical(self, "Asset Browser: Error", "Error reading assetTags.json. Asset tags will not be available.\nMaybe try restarting Source Filmmaker? Delete assetTags.json if possible.")

    def addTagsToList(self):
        # Add tags
        for tag in self.tags:
            # If tag is modelstack, add to model stack
            if tag.tagValue == "modelstack":
                for asset in tag.children:
                    # Get model name
                    basePath = asset.assetPath
                    basePath = basePath[basePath.find("\\")+1:]
                    basePath = basePath[basePath.find("\\")+1:]
                    baseName = basePath[basePath.rfind("/")+1:]
                    # Add model to creation stack
                    assetBrowser_globalModelStack.append(baseName)
            # Create item
            item_small = QtGui.QTreeWidgetItem(self.list)
            item_small.setText(0, tag.tagName)
            item_small.setIcon(0, QtGui.QPixmap.fromImage(QtGui.QImage(tag.tagImage)))
            item_small.setToolTip(0, tag.tagValue)

    def saveAssetTags(self):
        # Format: {"tags":[{"tagName": "Tag Name", "tagValue": "tagValue", "tagImage": assetBrowser_modPath + "/images/assettags/tag_sm.png", "children": ["./hl2/sound/error.wav"]}, ...]}
        # Open file
        f = open("assetTags.json", "w")
        # Create json from tags
        preJson = {}
        preJson["tags"] = []
        for tag in self.tags:
            tagObject = {}
            tagObject["tagName"] = tag.tagName
            tagObject["tagValue"] = tag.tagValue
            tagObject["tagImage"] = tag.tagImage
            tagObject["children"] = []
            for child in tag.children:
                tagObject["children"].append(child.assetPath)
            preJson["tags"].append(tagObject)
        # Write json to file
        json.dump(preJson, f)
        # Close file
        f.close()

    def listContextMenu(self):
        # Get item
        item = self.list.currentItem()
        # Check if item is in tag list
        for tag in self.tags:
            if tag.tagValue == item.toolTip(0):
                # Create menu
                menu = QtGui.QMenu()
                # Add tag text
                action = menu.addAction("Tag:")
                action.setEnabled(False)
                # Tag clear
                action = menu.addAction("Clear")
                action.triggered.connect(lambda: self.clearTag(tag))
                # Show menu
                menu.exec_(QtGui.QCursor.pos())
                return

    def clearTag(self, tag):
        # Remove children from tag
        tag.children = []
        # Save tags
        self.saveAssetTags()
        # Reload list
        self.list.setCurrentItem(self.list.currentItem())
        self.listItemClicked(self.list.currentItem())

    def pullLatestRelease(self):
        try:
            # Download from repo
            os.system("powershell -Command Invoke-WebRequest -URI \"" + assetBrowser_repo + "\" -OutFile \"assetBrowser.zip\"")
            # Unzip assetBrowser_repo
            zip_ref = zipfile.ZipFile("assetBrowser.zip", "r")
            zip_ref.extractall(assetBrowser_modPath)
            zip_ref.close()
            # Delete zip file
            os.remove("assetBrowser.zip")
            # Check version
            self.checkVersion(True)
        except:
            QtGui.QMessageBox.warning(self, "Asset Browser: Error", "Could not download latest release, please download the latest release from the GitHub repository.")

    def checkVersion(self, pulled=False):
        # Check txt file
        if not os.path.isfile(assetBrowser_modPath + "/version.txt"):
            if not pulled:
                self.pullLatestRelease()
            else:
                QtGui.QMessageBox.warning(self, "Asset Browser: Error", "Could not find version.txt, please download the latest release from the GitHub repository.")
                return
        # Open txt file
        f = open(assetBrowser_modPath + "/version.txt", "r")
        # Get version
        version = f.read()
        # Close file
        f.close()
        # Check version
        if version != assetBrowser_version and not pulled:
            # Ask user to update
            msgBox = QtGui.QMessageBox()
            msgBox.setText("An update is available for Asset Browser.")
            msgBox.setInformativeText("Would you like to update now?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
            msgBox.buttonClicked.connect(self.updateButtonClicked)
            msgBox.exec_()
        elif version != assetBrowser_version and pulled:
            # Version impossible to be met, assume future or dev version
            QtGui.QMessageBox.information(self, "Asset Browser: Update", "A development version of Asset Browser has been detected. Update could not succeed.")
            
    
    def updateButtonClicked(self, button):
        # Check button
        if button.text() == "&Yes":
            # Pull latest release
            self.pullLatestRelease()
try:
    # Create window
    assetBrowser_globalModelStack = []
    assetBrowserWindow=AssetBrowserWindow()
    sfmApp.RegisterTabWindow("WindowAssetBrowser", "Asset Browser", shiboken.getCppPointer( assetBrowserWindow )[0])
    sfmApp.ShowTabWindow("WindowAssetBrowser")

except Exception  as e:
    import traceback
    traceback.print_exc()        
    msgBox = QtGui.QMessageBox()
    msgBox.setText("Error: %s" % e)
    msgBox.exec_()
