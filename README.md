# Asset Browser

This is a simple asset browser script for Source Filmmaker.

![Screenshot of Asset Browser](https://i.imgur.com/vfnOvKv.png)

## Features

- Setting thumbnails (cannot generate thumbnails automatically)
- Saving/loading of asset index
- Ignore specific heavy folders
- Set depth level of indexing
- Search by keyword
- Filter by type and mod
- Browse folders in a tree view
- Double click on folders to expand them
- User-defined asset tags with custom icons (modifiable via JSON)
- Importing of several models at a time (using the "Model Stack" asset tag)
- Copying paths to clipboard
- Visiting the file in explorer
- Previewing of sounds (requires game window/F11)
- Viewing assets in external apps (HLMV, VTFEdit, etc.)
- Session loading
- Map loading

## Warning

This script pulls image data from a GitHub release using PowerShell.
I advise you to review the script contents before trusting it.

## How to Use

The asset browser can be opened using the `Scripts` tab > `KiwifruitDev` > `Asset Browser` in SFM.

Here are some rundowns of the workflow and features of the asset browser.

### Indexing

The first time you open the asset browser, no assets will be indexed. This gives you an opportunity to filter before indexing, or to load an existing index hive.

To index assets, click the `Refresh` button in the toolbar. This will recursively search through the `game` folder while filtering out anything specified.

### Saving and Loading Index Hives & Settings

Opening the `File Options` menu in the toolbar will provide options to save and load index hives and filter settings.

There are options for saving to a current file, saving to a new file, loading while merging, and loading while replacing.

Reload options are also available, which restores the index hive and filter settings to the last saved state.

Merging the index hive will append the new index hive to the current one, and will not remove any assets that are not in the new index hive.

Replacing the index hive will discard the current index hive and replace it with the new one.

Settings will always be replaced.

### Filtering

The filter settings can be found in the toolbar. You can filter by asset type, mod, root folder, and search term.

The search term is a simple string search, and will match any asset that contains the search term in its name.

Filtering after building the index hive will be non-destructive, and will only hide assets that do not match the filter.

Only filtered assets will be included in the index hive.

### Tags

Tags are a way to group assets together, or to mark assets as special.

At the moment, tags cannot be added or removed from the asset browser. They must be added to a specific JSON file located at `game/assetbrowser/assettags.json`.

Tags will forcibly add assets to the index hive, even if they are filtered out. This is to ensure that assets with tags are always available and can be excluded without filtering.

#### Adding Tags to Assets

To add a tag to an asset, right click on the asset and check the tag you want to add. The tag will be added to the asset.

If the asset is discarded through rebuilding the index hive or is otherwise unavailable, the tag will add the asset back to the index hive.

Only files can be tagged, folders will not provide tagging options.

Adding a tag will write to the tag JSON file, so it can be persisted between sessions.

#### Removing Tags from Assets

To remove a tag from an asset, right click on the asset and uncheck the tag you want to remove. The tag will be removed from the asset.

Removing a tag will write to the tag JSON file.

#### Creating Tags

To create a tag, add a new object to the `tags` array in the JSON file. The object must have the following properties:

- `tagName`: The name of the tag. This will be displayed in the asset browser.
  - Example: `My Custom Tag`
- `tagValue`: The value of the tag. This must be unique.
  - Example: `my_custom_tag`
- `tagImage`: The icon to use for the tag. This must be a valid path to an image file.
  - Example: `assetbrowser/images/assettags/tag_sm.png`
- `children`: An array of asset paths. Filling this out is optional, but it must be present as an array.
  - Example: `[".\\hl2\\models\\props_c17\\furniturefridge001a.mdl"]`

#### Removing Tags

To remove a tag, remove the object from the `tags` array in the JSON file.

### Previewing Assets

To preview an asset, double click on it. This will open the asset in its default application.

Previewing a model asset will prompt you with information about adding models to the current scene.

Single clicking on sound assets will play the sound in the game window. The game window (F11) must be open for this to work.

### Adding Models to the Scene

To add a model to the scene, add the special `Model Stack` tag to the asset.

Then, right click on any animation set within the `Animation Set Editor` window and click on `Rig` > `asset_browser_import_models`.

This bypasses an SFM limitation where models cannot be created by scripts dynamically.

### Copying Paths

Right clicking on an asset will provide a context menu with options to copy the relative or full path to the clipboard.

The relative path can be useful for copying paths to use in existing SFM import dialog boxes, such as when adding sounds to the timeline.

### Visiting in Explorer

To visit the location of an asset in explorer, right click on the asset and click `Open folder`.

For folder assets, this will open the folder itself.

For file assets, this will open the folder containing the file.

### Thumbnails

Thumbnails can be optionally added to assets.

First, you'll need an image. This can be an external image file or an image saved to the clipboard.

Then, right click on the asset and click `Set thumbnail from file` or `Set thumbnail from clipboard`.

The thumbnail will be saved to the `game/assetbrowser/thumbnails` folder with the directory structure of the asset.

To clear a thumbnail, right click on the asset and click `Clear thumbnail`. This will delete the thumbnail file.

There is no way to generate a thumbnail from an asset.

If you would like to quickly set thumbnails, you may use the Snipping Tool (Win + Shift + S) to take a screenshot of the asset preview and then set the thumbnail from the clipboard.

## Installation

1. Download the script from the [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2918590103)
2. Optional: Download the [latest release](https://github.com/KiwifruitDev/SFM-Asset-Browser/releases/latest) and extract it to `game/assetbrowser/`
3. Open the script in SFM using the `Scripts` tab > `KiwifruitDev` > `Asset Browser`
4. If the GitHub release is not present, the script will download it automatically

## Support Me

If you like my work, consider supporting me on [Ko-fi](https://ko-fi.com/kiwifruitdev) or [Patreon](https://www.patreon.com/kiwifruitdev).

## License

This project is licensed under the [MIT License](LICENSE).
