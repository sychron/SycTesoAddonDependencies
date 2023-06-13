# SycTesoAddonDependencies
Pytrhon script to check dependencies of addons for Elder Scrolls Online

USAGE

put the python script in a folder inside your Documents/Elder Scrolls Online folder, next to the live folder used by ESO.

Or put it where you want and change the addon path in the first lines of the script.

Documents
| Elder Scrolls Online
|| live
|| SycTesoAddonDependencies
||| dependencies.py

when running the script, it will scan the plugin text description files for all addons in the live/addons folder and compile information about what libraries are used by which plugin, divided between mandatory and optional libraries.

the script will also compile a list of all addons with missing mandatory or missing optional dependencies, as well as a list of all files assumed to be a library which are not used at all and can possibly be uninstalled.

Please note that there is a "isLibrary" tag in the description files, but this is not mandatory and many libraries do not have this tag. Therefore, libraries are also recognized by names starting with "lib". But this generates false positives, as some "libraries" are in actually more or less standalone addons, for example LibAddonKeybinds.

After running the script, you can use the compiled information to install needed dependencies, uninstall unused libraries etc.

COMPATIBILITY

This code was written and testes on Windows. I used python functions for all OS relevant differences, such as path processing, so the code should run on other operating systems as well. You might have to change the addon search path in the first lines of the script.

CURRENT STATUS

Currently the code is not operational as I'm refactoring.

Refactoring goals part 1 are:
- get a more robust and maintainable parser (done)
- get a better model class based data structure to handle more complex comparisons (done)
- handle dependency versions in parsing (done)
- handle version requirement differences in nested dependencies (done)
- handle nested mandatory dependencies of optional dependencies correctly (done)

Refactoring goals part 2 are:
- report unsatisfied mandatory dependencies
- report unused optional dependencies
- report unused libraries

IDEAS?

If this script is useful to you and/or you have any suggestion, please leave a comment or feel free to contribute.

I know this may not be the prettiest python code, but I decided to upload it now instead of having it sit on my disk for months waiting to be made pretty for release.

The code is modular, so I hope you can easily navigate it and modify functions or just copy functions you might find useful for your own projects. This script is MIT licensed, so feel free :)
