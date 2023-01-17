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
import vs, sfmApp, sfm, sfmUtils, json, os, urllib, zipfile, hashlib, re, subprocess, threading, time

assetBrowser_repo = "https://github.com/KiwifruitDev/SFM-Asset-Browser/releases/latest/download/assetbrowser.zip"
assetBrowser_modPath = "assetbrowser"
assetBrowser_globalModelStack = []
assetBrowser_version = "2"
assetBrowser_window = None

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
    def __init__(self, assetType, assetName, assetPath, mod, children):
        self.assetType = assetType
        self.assetName = assetName
        self.assetPath = assetPath
        self.mod = mod
        self.children = children
    assetType = "generic"
    assetName = ""
    assetPath = ""
    mod = ""
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
        self.assetIcons_Large["image"] = assetBrowser_modPath + "/images/assettypes/image_lg.png"
        self.assetIcons_Small["image"] = assetBrowser_modPath + "/images/assettypes/image_sm.png"
        self.assetIcons_Large["sound"] = assetBrowser_modPath + "/images/assettypes/sound_lg.png"
        self.assetIcons_Small["sound"] = assetBrowser_modPath + "/images/assettypes/sound_sm.png"
        self.assetIcons_Large["sfmsession"] = assetBrowser_modPath + "/images/assettypes/sfmsession_lg.png"
        self.assetIcons_Small["sfmsession"] = assetBrowser_modPath + "/images/assettypes/sfmsession_sm.png"
        # Init UI
        self.initUI()

    assetTypeBaseNames = [
        "folder",
        "generic",
        "map",
        "material",
        "mesh",
        "model",
        "particles",
        "sky",
        "text",
        "texture",
        "image",
        "sound",
        "sfmsession",
    ]

    firstDoubleClick = False

    assetTypes = {
        ".bsp": "map",

        ".vmt": "material",

        ".vtf": "texture",

        ".mdl": "model",

        ".vtx": "mesh",
        ".phy": "mesh",
        ".vvd": "mesh",

        ".pcf": "particles",

        ".txt": "text",
        ".cfg": "text",
        ".py": "text",

        ".dmx": "sfmsession",

        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".bmp": "image",
        ".tga": "image",
        ".gif": "image",

        ".wav": "sound",
        ".mp3": "sound",
    }

    forbiddenMods = [
        "bin",
        "sdktools",
        "screencast",
        "assetbrowser",
    ]

    forbiddenAssets = [
        ".git",
        "bin",
        "data",
        "classes",
        "addons",
        "cfg",
        "config",
        "demo",
        "friends",
        "elements/presets",
        "admin",
        "resource",
        "servers",
        "steam",
        "tools",
        "vgui",
        "media",
        "images",
        "scripts",
        "gfx",
        "shaders",
        "reslists",
        "scenes",
        "expressions",
        "vguiedit",
        "downloads",
        "metadata",
        "motionmappertemplates",
        "phonemeextractors",
        "qcgenerator",
        "vscripts",
        "playerclasses",
        "renders",
        "presets",
        "graphs",
        "mapsrc",
        "soundcache",
        "midi",
    ]

    rootAsset = Asset("folder", "Root", ".", "", [])

    everyAsset = {}
    
    tags = []

    filterTypes = [
        "folder",
        "map",
        "model",
        "particles",
        "sound",
        "sfmsession",
        "image",
    ]

    ignorables = [
        "materials",
    ]

    ignoreTypes = [
        "materials",
    ]

    modTypes = [
        "usermod",
    ]

    mods = []

    staticFolderIcon = None

    currentFolder = ""

    oldCurrentFolder = ""

    refreshActive = False

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
        # Get file extension
        fileExtension = os.path.splitext(assetFile)[1]
        # Check if file extension is in assetTypes
        if fileExtension in self.assetTypes:
            return self.assetTypes[fileExtension]
        return "generic"

    def getMods(self):
        # Get list of mods
        mods = os.listdir(".")
        # To lower case
        mods = [mod.lower() for mod in mods]
        # Remove forbidden mods
        for forbiddenMod in self.forbiddenMods:
            if forbiddenMod in mods:
                mods.remove(forbiddenMod)
        # Only add directories
        for mod in mods:
            if os.path.isdir(mod):
                self.mods.append(mod)
        # Set default mods
        #self.modTypes = self.mods

    def initUI(self):
        self.staticFolderIcon = QtGui.QPixmap.fromImage(QtGui.QImage(self.assetIcons_Small["folder"]))
        # Populate default filter types
        #self.populateDefaultFilterTypes()
        # Get mods
        self.getMods()
        # Create inner widget (stores grid, list, search, filters, and settings button)
        self.innerWidget = QtGui.QWidget()
        self.innerWidgetLayout = QtGui.QHBoxLayout()
        self.innerWidget.setLayout(self.innerWidgetLayout)
        self.innerWidgetLayout.setContentsMargins(10, 0, 10, 10)
        self.innerWidgetLayout.setSpacing(10)
        self.innerWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create list on left side (allow resizing with splitter)
        self.listWidget = QtGui.QWidget()
        self.listWidgetLayout = QtGui.QVBoxLayout()
        self.listWidget.setLayout(self.listWidgetLayout)
        self.listWidget.setMinimumWidth(200)
        self.listWidget.setMaximumWidth(2000)
        self.listWidget.setMinimumHeight(400)
        self.listWidget.setMaximumHeight(2000)
        self.listWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.listWidgetLayout.setContentsMargins(0,0,0,0)
        self.listWidgetLayout.setSpacing(0)
        self.listWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create grid on right side (doesn't allow resizing, sticks to list)
        self.gridWidget = QtGui.QWidget()
        self.gridWidgetLayout = QtGui.QVBoxLayout()
        self.gridWidget.setLayout(self.gridWidgetLayout)
        self.gridWidget.setMinimumWidth(200)
        self.gridWidget.setMaximumWidth(2000)
        self.gridWidget.setMinimumHeight(400)
        self.gridWidget.setMaximumHeight(2000)
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
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        # Add to inner widget
        self.innerWidgetLayout.addWidget(self.splitter)
        # Set self (outer) widget (stores inner widget and toolbar)
        self.outerWidgetLayout = QtGui.QVBoxLayout()
        self.outerWidgetLayout.setContentsMargins(0,0,0,0)
        self.outerWidgetLayout.setSpacing(0)
        self.outerWidgetLayout.setAlignment(QtCore.Qt.AlignTop)
        # Create toolbar
        self.toolbar = QtGui.QWidget()
        self.toolbarLayout = QtGui.QHBoxLayout()
        self.toolbarLayout.setContentsMargins(10,10,10,10)
        self.toolbarLayout.setSpacing(10)
        self.toolbarLayout.setAlignment(QtCore.Qt.AlignLeft)
        # Create search box
        self.searchBox = QtGui.QLineEdit(self.toolbar)
        self.searchBox.setPlaceholderText("Search")
        self.searchBox.setToolTip("Search for a file.")
        self.searchBox.textChanged.connect(self.searchBoxTextChanged)
        self.toolbarLayout.addWidget(self.searchBox)
        # Create index amount integer box label
        self.indexAmountBoxLabel = QtGui.QLabel(self.toolbar)
        self.indexAmountBoxLabel.setText("Max Depth:")
        self.toolbarLayout.addWidget(self.indexAmountBoxLabel)
        # Create index amount integer box
        self.indexAmountBox = QtGui.QSpinBox(self.toolbar)
        self.indexAmountBox.setRange(1, 8192)
        self.indexAmountBox.setValue(4)
        self.indexAmountBox.setToolTip("Maximum folder depth. Setting this value too high with too many filters/mods selected will take a LONG time to refresh.")
        self.toolbarLayout.addWidget(self.indexAmountBox)
        # Create filter list button
        self.filterListButton = QtGui.QToolButton(self.toolbar)
        self.filterListButton.setText("Filters (%d)" % len(self.filterTypes))
        self.filterListButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.filterListButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.filterListButton.setToolTip("These are the different types of files. Only add what you think you need.")
        self.filterListButtonMenu = QtGui.QMenu()
        self.filterListButton.setMenu(self.filterListButtonMenu)
        self.filterListButtonMenu.aboutToShow.connect(self.filterListButtonMenuAboutToShow)
        self.toolbarLayout.addWidget(self.filterListButton)
        # Create mod list button
        self.modListButton = QtGui.QToolButton(self.toolbar)
        self.modListButton.setText("Mods (%d)" % len(self.modTypes))
        self.modListButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.modListButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.modListButton.setToolTip("Mods are search path folders. Only add what you think you need.")
        self.modListButtonMenu = QtGui.QMenu()
        self.modListButton.setMenu(self.modListButtonMenu)
        self.modListButtonMenu.aboutToShow.connect(self.modListButtonMenuAboutToShow)
        self.toolbarLayout.addWidget(self.modListButton)
        # Create ignore button
        self.ignoreButton = QtGui.QToolButton(self.toolbar)
        self.ignoreButton.setText("Ignore (%d)" % len(self.ignoreTypes))
        self.ignoreButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.ignoreButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.ignoreButton.setToolTip("Ignore specific root folders (i.e materials).")
        self.ignoreButtonMenu = QtGui.QMenu()
        self.ignoreButton.setMenu(self.ignoreButtonMenu)
        self.ignoreButtonMenu.aboutToShow.connect(self.ignoreButtonMenuAboutToShow)
        self.toolbarLayout.addWidget(self.ignoreButton)
        # Save/load settings button
        self.saveButton = QtGui.QToolButton(self.toolbar)
        self.saveButton.setText("Save")
        self.saveButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.saveButton.setToolTip("Save settings and current index hive to a file.")
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.toolbarLayout.addWidget(self.saveButton)
        self.loadButton = QtGui.QToolButton(self.toolbar)
        self.loadButton.setText("Load")
        self.loadButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.loadButton.setToolTip("Load settings and index hive from a file.")
        self.loadButton.clicked.connect(self.loadButtonClicked)
        self.toolbarLayout.addWidget(self.loadButton)
        # Create refresh button
        self.refreshButton = QtGui.QToolButton(self.toolbar)
        self.refreshButton.setText("Refresh")
        self.refreshButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.refreshButton.setToolTip("Refresh or cancel refreshing the index hive.")
        self.refreshButton.clicked.connect(self.refreshButtonClicked)
        self.toolbarLayout.addWidget(self.refreshButton)
        # Create status text
        self.statusText = QtGui.QLabel(self.toolbar)
        self.statusText.setText("Ready")
        self.toolbarLayout.addWidget(self.statusText)
        # Create spacer
        self.toolbarSpacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.toolbarLayout.addItem(self.toolbarSpacer)
        # Set toolbar layout
        self.toolbar.setLayout(self.toolbarLayout)
        # Add toolbar to outer widget
        self.outerWidgetLayout.addWidget(self.toolbar)
        # Add inner widget to outer widget
        self.outerWidgetLayout.addWidget(self.innerWidget)
        # Set layout
        self.setLayout(self.outerWidgetLayout)
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
        #for item in os.listdir("."):
            #fullpath = os.path.join(".", item)
            #if os.path.isdir(fullpath):
                #self.recursiveScan(fullpath) # Add mod folder
        # Sort alphabetically
        self.list.sortItems(0, QtCore.Qt.AscendingOrder)
        # Check version
        self.checkVersion()
        # Add dummy root item
        dummy = QtGui.QTreeWidgetItem()
        dummy.setText(0, "Root (Click refresh to populate)")
        dummy.setIcon(0, QtGui.QPixmap.fromImage(QtGui.QImage(self.assetIcons_Small["folder"])))
        self.list.addTopLevelItem(dummy)
        # Update tags
        self.loadAssetTags()
        # Update list for tags
        self.addTagsToList()
        # Update list
        #self.recursiveUpdateList()
        # Expand top level items
        for i in range(self.list.topLevelItemCount()):
            self.list.topLevelItem(i).setExpanded(True)
        # Click on first item
        self.list.setCurrentItem(self.list.topLevelItem(0))
        self.listItemClicked(self.list.topLevelItem(0))

    def saveButtonClicked(self):
        # Serialize settings
        settings = {}
        settings["ignorables"] = self.ignorables
        settings["ignoreTypes"] = self.ignoreTypes
        settings["modTypes"] = self.modTypes
        settings["mods"] = self.mods
        # Serialize root asset
        rootAsset = {}
        rootAsset["assetName"] = self.rootAsset.assetName
        rootAsset["assetType"] = self.rootAsset.assetType
        rootAsset["assetPath"] = self.rootAsset.assetPath
        rootAsset["mod"] = self.rootAsset.mod
        rootAsset["children"] = self.rootAsset.children
        # Serialize assets
        assets = {}
        for uuid, asset in self.everyAsset.items():
            assets[uuid] = {}
            assets[uuid]["assetName"] = asset.assetName
            assets[uuid]["assetType"] = asset.assetType
            assets[uuid]["assetPath"] = asset.assetPath
            assets[uuid]["mod"] = asset.mod
            assets[uuid]["children"] = asset.children
        # Serialize to file
        data = {}
        data["settings"] = settings
        data["rootAsset"] = rootAsset
        data["assets"] = assets
        # Ask where to save
        filename, type = QtGui.QFileDialog.getSaveFileName(self, "Save index hive to a file", assetBrowser_modPath, "JavaScript Object Notation (*.json)")
        if filename:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)

    def loadButtonClicked(self):
        # Ask where to load from
        filename, type = QtGui.QFileDialog.getOpenFileName(self, "Load index hive from a file", assetBrowser_modPath, "JavaScript Object Notation (*.json)")
        if filename:
            with open(filename, "r") as f:
                data = json.load(f)
            # Deserialize settings
            self.ignorables = data["settings"]["ignorables"]
            self.ignoreTypes = data["settings"]["ignoreTypes"]
            self.modTypes = data["settings"]["modTypes"]
            self.mods = data["settings"]["mods"]
            # Set button text
            self.ignoreButton.setText("Ignore (%d)" % len(self.ignorables))
            self.modListButton.setText("Mods (%d)" % len(self.mods))
            self.filterListButton.setText("Filters (%d)" % len(self.ignoreTypes))
            # Deserialize root asset
            self.rootAsset = Asset(data["rootAsset"]["assetType"], data["rootAsset"]["assetName"], data["rootAsset"]["assetPath"], data["rootAsset"]["mod"], data["rootAsset"]["children"])
            # Deserialize assets
            self.everyAsset = {}
            for uuid, assetData in data["assets"].items():
                asset = Asset(assetData["assetType"], assetData["assetName"], assetData["assetPath"], assetData["mod"], assetData["children"])
                self.everyAsset[uuid] = asset
            self.list.clear()
            # Update list
            self.recursiveUpdateList()
            # Update tags
            self.loadAssetTags()
            # Update list for tags
            self.addTagsToList()
            # Expand top level items
            for i in range(self.list.topLevelItemCount()):
                self.list.topLevelItem(i).setExpanded(True)
            
    def ignoreButtonMenuAboutToShow(self):
        # Clear menu
        self.ignoreButtonMenu.clear()
        # Add ignore types
        for ignoreType in self.ignorables:
            action = QtGui.QAction(ignoreType, self.ignoreButtonMenu)
            action.setCheckable(True)
            action.setChecked(ignoreType in self.ignoreTypes)
            action.triggered.connect(self.ignoreButtonMenuActionTriggered)
            self.ignoreButtonMenu.addAction(action)

    def ignoreButtonMenuActionTriggered(self):
        action = self.sender()
        if action.isChecked():
            self.ignoreTypes.append(action.text())
        else:
            self.ignoreTypes.remove(action.text())
        # Update text
        self.ignoreButton.setText("Ignore (%d)" % len(self.ignoreTypes))

    def populateDefaultFilterTypes(self):
        self.filterTypes = []
        for assetType in self.assetTypeBaseNames:
            self.filterTypes.append(assetType)

    def filterListButtonMenuAboutToShow(self):
        # Clear menu
        self.filterListButtonMenu.clear()
        # Add filter types
        for assetType in self.assetTypeBaseNames:
            action = QtGui.QAction(assetType, self.filterListButtonMenu)
            action.setCheckable(True)
            action.setChecked(assetType in self.filterTypes)
            action.setIcon(QtGui.QIcon(self.assetIcons_Small[assetType]))
            action.triggered.connect(self.filterListButtonMenuActionTriggered)
            self.filterListButtonMenu.addAction(action)

    def modListButtonMenuAboutToShow(self):
        # Clear menu
        self.modListButtonMenu.clear()
        # Add mod types
        for modType in self.mods:
            action = QtGui.QAction(modType, self.modListButtonMenu)
            action.setCheckable(True)
            action.setChecked(modType in self.modTypes)
            action.triggered.connect(self.modListButtonMenuActionTriggered)
            self.modListButtonMenu.addAction(action)

    def modListButtonMenuActionTriggered(self):
        # Update mod types
        self.modTypes = []
        for action in self.modListButtonMenu.actions():
            if action.isChecked():
                self.modTypes.append(action.text())
        # Update mod list button text
        self.modListButton.setText("Mods (%d)" % len(self.modTypes))
        searchText = self.searchBox.text()
        if searchText != "":
            self.searchBoxTextChanged(searchText)
        else:
            curitem = self.list.currentItem()
            if curitem is not None:
                self.listItemClicked(curitem)

    def filterListButtonMenuActionTriggered(self):
        # Update filter types
        self.filterTypes = []
        for action in self.filterListButtonMenu.actions():
            if action.isChecked():
                self.filterTypes.append(action.text())
        # Update filter list button text
        self.filterListButton.setText("Filters (%d)" % len(self.filterTypes))
        searchText = self.searchBox.text()
        if searchText != "":
            self.searchBoxTextChanged(searchText)
        else:
            self.listItemClicked(self.list.currentItem())

    def searchBoxTextChanged(self, text):
        self.gridList.clear()
        # Disable list if text is not empty
        if text != "":
            self.list.setEnabled(False)
            self.oldCurrentFolder = self.currentFolder
            self.currentFolder = ""
            # Update grid list
            for assetUuid, asset in self.everyAsset.items():
                if text.lower() in asset.assetName.lower():
                    if asset.assetType in self.filterTypes and asset.mod in self.modTypes:
                        # Add to grid list
                        item = QtGui.QListWidgetItem()
                        item.setText(asset.assetName)
                        item.setData(QtCore.Qt.DecorationRole, QtGui.QImage(self.assetIcons_Large[asset.assetType]))
                        item.setToolTip(asset.assetPath)
                        self.gridList.addItem(item)
        else:
            self.list.setEnabled(True)
            self.currentFolder = self.oldCurrentFolder
            # Re-populate grid list
            self.listItemClicked(self.list.currentItem())

    def refreshButtonClicked(self):
        if self.refreshActive:
            self.refreshActive = False
        else:
            self.statusText.setText("Refreshing...")
            # Set text to cancel
            self.refreshButton.setText("Cancel")
            # Disable buttons
            self.ignoreButton.setEnabled(False)
            self.filterListButton.setEnabled(False)
            self.modListButton.setEnabled(False)
            self.indexAmountBox.setEnabled(False)
            self.saveButton.setEnabled(False)
            self.loadButton.setEnabled(False)
            # Clear list
            self.list.clear()
            # Clear grid
            self.gridList.clear()
            # Clear ignorables
            self.ignorables = []
            # Clear assets
            self.rootAsset.children = []
            self.everyAsset = {}
            # Get folders in .
            self.refreshActive = True
            for item in os.listdir("."):
                fullpath = os.path.join(".", item)
                if os.path.isdir(fullpath):
                    self.recursiveScan(fullpath) # Add mod folder
            # Update tags
            self.loadAssetTags()
            # Update list for tags
            self.addTagsToList()
            # Update list
            self.recursiveUpdateList()
            self.refreshActive = False
            # Merge ignorables with ignoredTypes
            self.ignorables = list(set(self.ignoreTypes + self.ignorables))
            self.statusText.setText("Complete")
            self.refreshButton.setText("Refresh")
            self.ignoreButton.setEnabled(True)
            self.filterListButton.setEnabled(True)
            self.modListButton.setEnabled(True)
            self.indexAmountBox.setEnabled(True)
            self.saveButton.setEnabled(True)
            self.loadButton.setEnabled(True)

    def getUUID(self, path):
        # Get uuid from path
        uuid = hashlib.md5(path).hexdigest()
        return uuid

    def recursiveScan(self, path, parent=None, depth=0):
        # Scan the given path recursively
        for item in os.listdir(path):
            # Update qt
            sfmApp.ProcessEvents()
            # Check if we should stop
            if not self.refreshActive:
                return
            fullpath = os.path.join(path, item)
            assetType = self.getTypeOfAsset(item, fullpath)
            # Is type filtered?
            if assetType != "folder" and assetType not in self.filterTypes:
                continue
            # Don't even parse generic assets
            #if assetType == "generic":
                #continue
            # Make uuid for asset
            nonModPath = fullpath[fullpath.find("\\")+1:]
            nonModPath = nonModPath[nonModPath.find("\\")+1:]
            nonModPath = nonModPath.replace("\\", "/")
            # Remove .\ from start of path
            modPath = fullpath.replace("\\", "/")
            modPath = modPath[modPath.find("/")+1:]
            # Regex /.* to get the mod name
            modPath = re.sub("/.*", "", modPath)
            # Check if in forbiddenMods
            if modPath.lower() in self.forbiddenMods:
                continue
            # Is mod filtered?
            if modPath not in self.modTypes:
                continue
            # Check if second folder is ignored
            if nonModPath.find("/") != -1:
                secondFolder = nonModPath[:nonModPath.find("/")]
                if secondFolder.lower() in self.ignoreTypes:
                    continue
            uuid = self.getUUID(nonModPath)
            asset = Asset(assetType, item, fullpath, modPath, [])
            # Does asset uuid already exist?
            taken = False
            for uuid2 in self.everyAsset.keys():
                if uuid2 == uuid:
                    taken = True
                    break
            # Check if forbidden
            if nonModPath.lower() in self.forbiddenAssets:
                continue
            # Only types allowed in root are folders
            if parent == None and assetType != "folder":
                continue
            # Add asset to parent
            if not taken:
                if parent:
                    parent.children.append(uuid)
                else:
                    self.rootAsset.children.append(uuid)
                # Add to all assets
                self.everyAsset[uuid] = asset
            else:
                # Get existing asset
                asset = self.getAssetFromUUID(uuid)
            # Update list
            self.recursiveUpdateList()
            # Update grid
            curitem = self.list.currentItem()
            if curitem is not None:
                # Get mod path but remove the file name
                modPathWithoutFile = re.sub("/[^/]*$", "", nonModPath)
                # Replace / with \ 
                modPathWithoutFile = modPathWithoutFile.replace("/", "\\")
                # Add .\modPath
                modPathWithoutFile = u".\\" + modPath + "\\" + modPathWithoutFile
                # Check if current folder is the same as the mod path
                if self.currentFolder == modPathWithoutFile:
                    self.listItemClicked(curitem)
            # Check if asset is a folder
            if asset.assetType == "folder":
                if depth <= self.indexAmountBox.value() - 1:
                    # Scan folder
                    self.recursiveScan(fullpath, asset, depth+1)

    def getAssetFromUUID(self, uuid):
        for assetUuid, asset in self.everyAsset.items():
            if assetUuid == uuid:
                return asset
        return None

    def recursiveUpdateList(self, assetParent=None, itemParent=None, depth=0):
        if assetParent == None:
            assetParent = self.rootAsset
        depthText = ""
        for i in range(depth):
            depthText += "- "
        # Don't add files
        if assetParent.assetType != "folder":
            return
        # First, check to see if asset is in list already
        item = self.recursiveGetAssetListItem(depthText + assetParent.assetName)
        if item:
            # Update item
            item.setToolTip(0, assetParent.assetPath)
            # Add children
            for childUuid in assetParent.children:
                child = self.getAssetFromUUID(childUuid)
                self.recursiveUpdateList(child, item, depth+1)
            return
        # Add asset to list
        item_small = QtGui.QTreeWidgetItem(itemParent)
        item_small.setText(0, depthText + assetParent.assetName)
        item_small.setIcon(0, self.staticFolderIcon)
        item_small.setToolTip(0, assetParent.assetPath)
        # Add to list
        if itemParent:
            itemParent.addChild(item_small)
        else:
            self.list.addTopLevelItem(item_small)
        # If 0 depth, expand
        if depth == 0:
            item_small.setExpanded(True)
        elif depth == 1:
            # Add to ignore list
            self.ignorables.append(assetParent.assetName)
        # Add children
        for childUuid in assetParent.children:
            child = self.getAssetFromUUID(childUuid)
            self.recursiveUpdateList(child, item_small, depth+1)

    def recursiveGetAssetListItem(self, text, item=None):
        # Loop through all items
        if item is None:
            for i in range(self.list.topLevelItemCount()):
                item = self.list.topLevelItem(i)
                # Check if item is valid
                if item is None:
                    continue
                # Check if item is asset
                if item.text(0) == text:
                    return item
                # Check children recursively
                child = self.recursiveGetAssetListItem(text, item)
                if child:
                    return child
            return None
        else:
            # Check if item is asset
            if item.text(0) == text:
                return item
            # Check children recursively
            for i in range(item.childCount()):
                child = item.child(i)
                # Check if item is asset
                if child.text(0) == text:
                    return child
                # Check children recursively
                child = self.recursiveGetAssetListItem(text, child)
                if child:
                    return child
        return None
            
    def recursiveGetAssetFromPath(self, path, assetParent=None):
        nonModPath = path[path.find("\\")+1:]
        nonModPath = nonModPath[nonModPath.find("\\")+1:]
        nonModPath = nonModPath.replace("\\", "/")
        uuid = self.getUUID(nonModPath)
        return self.getAssetFromUUID(uuid)

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
        if asset.assetType == "sound":
            # Play sound
            sfm.console("play " + basePath)

    def assetDoubleClicked(self, asset):
        # Get base path (remove .\*\*\)
        basePath = asset.assetPath
        # Remove .\ from path
        rootPath = basePath[2:]
        # Add cwd to path
        rootPath = os.path.join(os.getcwd(), basePath)
        # SFM sessions don't have a base path and materials/textures need cwd
        basePath = basePath[basePath.find("\\")+1:]
        basePath = basePath[basePath.find("\\")+1:]
        # Models use a prefix, others don't
        if asset.assetType != "model":
            basePath = basePath[basePath.find("\\")+1:]
            # Parse \ as /
            basePath = basePath.replace("\\", "/")
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
            # Show information on how to import a model on first double click
            if not self.firstDoubleClick:
                QtGui.QMessageBox.information(self, "Asset Browser: Model Import", "Due to an SFM limitation, models cannot be imported directly.\n\nTo import models, right click and check the \"Model Stack\" tag, then run\nthe \"asset_browser_import_models\" rig script from any animation set.\n\nModels can be imported in bulk, even outside of filtering.\n\nThis message will not appear again, models will open in HLMV instead.")
                self.firstDoubleClick = True
            # Open in HLMV
            hlmv = os.getcwd() + "\\bin\\hlmv.exe"
            if os.path.exists(hlmv):
                subprocess.Popen([hlmv, rootPath])
            else:
                os.startfile(rootPath)
        elif asset.assetType == "sfmsession":
            # Close current session and open new one
            sfmApp.CloseDocument(forceSilent=False)
            sfmApp.OpenDocument(rootPath)
        elif asset.assetType == "folder":
            # Double click in list
            listItem = self.list.currentItem()
            if listItem:
                # Expand if collapsed
                if not listItem.isExpanded():
                    listItem.setExpanded(True)
                # Find item with same name
                for i in range(listItem.childCount()):
                    child = listItem.child(i)
                    # Regex to get base name
                    baseName = re.sub("/.*", "", asset.assetName)
                    text = child.text(0)
                    # Remove depth from text
                    while text[0] == "-":
                        text = text[2:]
                    # Compare
                    if text == baseName:
                        self.list.setCurrentItem(child)
                        self.listItemClicked(child)
                        break
                #QtGui.QMessageBox.information(self, "Asset Browser: Error", "This folder is empty using the current filter settings.")
        else:
            # Open in external editor (vtfedit? vscode?)
            os.startfile(rootPath)

    def listItemClicked(self, item):
        self.currentFolder = item.toolTip(0)
        asset = None
        # Get asset from path
        if item.toolTip(0) == ".":
            asset = self.rootAsset
        else:
            asset = self.recursiveGetAssetFromPath(item.toolTip(0))
        if asset:
            # Reset grid icons and add new ones
            self.gridList.clear()
            for childUuid in asset.children:
                child = self.getAssetFromUUID(childUuid)
                if child:
                    # Is asset filtered?
                    if child.assetType in self.filterTypes and child.mod in self.modTypes:
                        item = QtGui.QListWidgetItem()
                        item.setText(child.assetName)
                        item.setData(QtCore.Qt.DecorationRole, QtGui.QImage(self.assetIcons_Large[child.assetType]))
                        item.setToolTip(child.assetPath)
                        self.gridList.addItem(item)
        else:
            # Presume tag was clicked
            # Reset grid icons and add new ones
            self.gridList.clear()
            for tag in self.tags:
                if tag.tagValue == item.toolTip(0):
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
        if not item:
            return
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip())
        if asset:
            # Create context menu
            menu = QtGui.QMenu()
            # Add actions text
            action = QtGui.QAction(asset.assetType == "folder" and "Folder:" or "File:", self)
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
            # Add copy relative path action
            action = QtGui.QAction("Copy relative path", self)
            action.triggered.connect(lambda: self.copyRelativePath(asset))
            menu.addAction(action)
            # Add open folder action
            action = QtGui.QAction("Open folder", self)
            action.triggered.connect(lambda: self.openFolder(asset))
            menu.addAction(action)
            # Add tag text if not a folder
            if asset.assetType != "folder":
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
            # Add mod text
            action = QtGui.QAction("Mod: " + asset.mod, self)
            action.setEnabled(False)
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

    def copyRelativePath(self, asset):
        # Remove .\ from path
        path = asset.assetPath[2:]
        # Remove mod from path
        path = path[path.find("\\"):]
        # Trim leading /
        path = path[1:]
        # Remove first directory from path
        path = path[path.find("\\"):]
        # Trim leading /
        path = path[1:]
        # Replace \ with /
        path = path.replace("\\", "/")
        # Copy path to clipboard
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(path)

    def openFolder(self, asset):
        # Get folder path
        folderPath = asset.assetPath
        # If asset is not a folder, get containing folder
        if asset.assetType != "folder":
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
        # Reload list if search is empty
        if self.searchBox.text() == "":
            self.list.setCurrentItem(self.list.currentItem())
            self.listItemClicked(self.list.currentItem())
    
    def gridItemDoubleClicked(self, item):
        # Get asset from path
        asset = self.recursiveGetAssetFromPath(item.toolTip())
        if asset:
            self.assetDoubleClicked(asset)
        
    # Load asset tags from json file
    def loadAssetTags(self):
        # Format: {"tags":[{"tagName": "Tag Name", "tagValue": "tagValue", "tagImage": assetBrowser_modPath + "/images/assettags/tag_sm.png", "children": ["./hl2/sound/error.wav"]}, ...]}
        # Open file if it exists
        if not os.path.isfile(assetBrowser_modPath + "/assetTags.json"):
            # Create file
            f = open(assetBrowser_modPath + "/assetTags.json", "w")
            # Create json from defaultTags
            # HACK: This doesn't work anymore, so we're writing it directly for now.
            #preJson = {}
            #preJson["tags"] = []
            #for tag in self.defaultTags:
                #tagObject = {}
                #tagObject["tagName"] = tag.tagName
                #tagObject["tagValue"] = tag.tagValue
                #tagObject["tagImage"] = tag.tagImage
                #tagObject["children"] = []
                #for child in tag.children:
                    #tagObject["children"].append(child.assetPath)
                #preJson["tags"].append(tagObject)
            # Write json to file
            try:
                #json.dump(preJson, f)
                jsonstr = "{\"tags\": [{\"tagValue\": \"favorites\", \"children\": [], \"tagName\": \"Favorites\", \"tagImage\": \"assetbrowser/images/assettags/favorites_sm.png\"}, {\"tagValue\": \"red\", \"children\": [], \"tagName\": \"Red\", \"tagImage\": \"assetbrowser/images/assettags/red_sm.png\"}, {\"tagValue\": \"green\", \"children\": [], \"tagName\": \"Green\", \"tagImage\": \"assetbrowser/images/assettags/green_sm.png\"}, {\"tagValue\": \"blue\", \"children\": [], \"tagName\": \"Blue\", \"tagImage\": \"assetbrowser/images/assettags/blue_sm.png\"}, {\"tagValue\": \"modelstack\", \"children\": [], \"tagName\": \"Model Stack\", \"tagImage\": \"assetbrowser/images/assettags/modelstack_sm.png\"}]}"
                f.write(jsonstr)
                f.close()
            except:
                if f:
                    f.close()
                QtGui.QMessageBox.critical(self, "Asset Browser: Error", "Error writing to assetTags.json. Asset tags will not be available.\nMaybe try restarting Source Filmmaker? Delete assetTags.json if possible.")
        #try:
        f = open(assetBrowser_modPath + "/assetTags.json", "r")
        # Parse json
        data = json.load(f)
        # Close file
        f.close()
        # Clear tags
        self.tags = []
        # Add tag to "tags" list
        for tag in data["tags"]:
            # Get assets from children
            assets = []
            for child in tag["children"]:
                # Replace / with \
                child = child.replace("/", "\\")
                asset = self.recursiveGetAssetFromPath(child)
                if not asset:
                    # Create asset just for tag purposes
                    cwd = os.getcwd()
                    # Remove .\\ from path
                    if child[0:2] == ".\\":
                        child = child[2:]
                    # Get asset path
                    fullPath = os.path.join(cwd, child)
                    # Get asset name
                    baseName = fullPath[fullPath.rfind("\\")+1:]
                    # Get asset type
                    assetType = self.getTypeOfAsset(baseName, fullPath)
                    # Make uuid for asset
                    nonModPath = fullPath[fullPath.find("\\")+1:]
                    nonModPath = nonModPath[nonModPath.find("\\")+1:]
                    nonModPath = nonModPath.replace("\\", "/")
                    modPath = child.replace("\\", "/")
                    modPath = modPath[modPath.find("/")+1:]
                    # Regex /.* to get the mod name
                    modPath = re.sub("/.*", "", modPath)
                    # Create asset
                    asset = Asset(assetType, baseName, fullPath, modPath, [])
                    # Get uuid
                    uuid = self.getUUID(nonModPath)
                    # Add asset to self.everyAsset
                    self.everyAsset[uuid] = asset
                assets.append(asset)
            # Add tag
            self.tags.append(Tag(tag["tagName"], tag["tagValue"], tag["tagImage"], assets))
        #except:
            #QtGui.QMessageBox.critical(self, "Asset Browser: Error", "Error reading assetTags.json. Asset tags will not be available.\nMaybe try restarting Source Filmmaker? Delete assetTags.json if possible.")

    def addTagsToList(self):
        # Clear model stack
        assetBrowser_globalModelStack = []
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
        f = open(assetBrowser_modPath + "/assetTags.json", "w")
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
    # Create window if it doesn't exist
    assetBrowser_globalModelStack = []
    globalAssetBrowser = globals().get("assetBrowserWindow")
    if globalAssetBrowser is None:
        assetBrowserWindow=AssetBrowserWindow()
        sfmApp.RegisterTabWindow("WindowAssetBrowser", "Asset Browser", shiboken.getCppPointer( assetBrowserWindow )[0])
        sfmApp.ShowTabWindow("WindowAssetBrowser")
    else:
        dialog = QtGui.QMessageBox.warning(None, "Asset Browser: Error", "Asset Browser is already open.\n\nIf you are a developer, click Yes to forcibly open a new instance.\n\nOtherwise, click No to close this message.", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if dialog == QtGui.QMessageBox.Yes:
            assetBrowserWindow=AssetBrowserWindow()
            sfmApp.RegisterTabWindow("WindowAssetBrowser", "Asset Browser", shiboken.getCppPointer( assetBrowserWindow )[0])
            sfmApp.ShowTabWindow("WindowAssetBrowser")

except Exception  as e:
    import traceback
    traceback.print_exc()        
    msgBox = QtGui.QMessageBox()
    msgBox.setText("Error: %s" % e)
    msgBox.exec_()
