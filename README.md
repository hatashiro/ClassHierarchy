ClassHierarchy
--------------

Class Hierarchy with CTags for Sublime Text 2

Screenshots
-----------

![screenshot1](https://raw.github.com/noraesae/ClassHierarchy/screenshots/screenshot1.png)
![screenshot2](https://raw.github.com/noraesae/ClassHierarchy/screenshots/screenshot2.png)

Prerequirement
--------------

This package uses [ctags](http://ctags.sourceforge.net/) to parse class hierarchy from projects.
[ctags](http://ctags.sourceforge.net/) should be installed before using this package.

Installation
------------

You can manually install the package.
```
cd /path/to/Sublime Text 2/Packages
git clone https://github.com/noraesae/ClassHierarchy.git
```

Or just install with [Sublime Text 2 Package Control](http://wbond.net/sublime_packages/package_control). The package is registered as "ClassHierarchy".

How to Use
----------

About commands, please refer to [Commands](#commands).

##### In the hierarchy view of the class you selected...

* Click: fold / unfold the file list of the symbol.
* Double-click: move to the file.


Commands
--------

### Re/Build Ctags for Class Hierarchy.
Re/Building ctags file should be done before any other command.
This command creates **.tags-hierarchy** file in project directory.  
*You can ignore this file with local or global ignorance settings in version controls.*

##### Key Command
`ctrl+shift+h` `ctrl+shift+b`

##### Window Command
*ClassHierarchy: Re/Build Ctags for Class Hierarchy*

### Re/Load Hierarchy Tree
Re/Load hierarchy tree object from the ctags file created by the build command.
To show downward or upward hieararchy, the tree object should be loaded.  
When you run hierarchy commands without the tree object loaded, this command will be executed automatically.

##### Key Command
`ctrl+shift+h` `ctrl+shift+t`

##### Window Command
*ClassHierarchy: Re/Load Hierarchy Tree*

### Show Upward Hierarchy
Show the class's ancestors. The class name used in the command will be the word under cursor.  
If the word under cursor is not in the class hierarchy tree, an input panel is displayed to select the class.
The panel is also displayed when the command is executed with window command.  
When the word is in the tree but there's no ancestor, a status message is displayed.

##### Key Command
`ctrl+shift+h` `ctrl+shift+u`

##### Window Command
*ClassHierarchy: Show Upward Hierarchy*

### Show Downward Hierarchy
Same with **Show Upward Hierarchy** except that this command shows the class's descendants.

##### Key Command
`ctrl+shift+h` `ctrl+shift+d`

##### Window Command
*ClassHierarchy: Show Downward Hierarchy*

Settings
-----------

### Default Settings
```json
{
    "ctags_command": "ctags -R --fields=+i-afkKlmnsSzt",
    "ctags_file": ".tags-hierarchy",
    "tab_size": 4
}
```

##### ctags_command
Ctags command to be executed with *Re/Build Ctags for Class Hierarchy* command. `-f` argument will be ignored.

##### ctags_file
File path to create ctags file in. The path can be absolute or relative to project directory.

##### tab_size
Tab size used to show class hierarchy.

### Custom Settings

When you want to set the settings of ClassHierarchy in **User** or **Project** settings,
you should append **class_hierarchy_** to the name of the setting like below.

```json
{
    "class_hierarchy_ctags_command": "ctags -R --fields=+i-afkKlmnsSzt --exclude=.git",
    "class_hierarchy_ctags_file": "tags-ch",
    "class_hierarchy_tab_size": 2
}
```

Windows Support
---------------
This package may or may not support window environment.
I think it may work if ctags in Windows works same with other environments, but it's not tested.
I have no Windows environment and no plan to implement Windows support when the package doesn't work in Windows.  
But you can freely fork this project and fix the program without any restriction.  
And I'll *really really* appreciate if there's any contibution of this issue.

Contribution
------------

I *really* welcome contributions! Please feel free to fork and issue pull requests when...

* You have a very nice idea to improve this plugin!
* You found a bug!
* You're good at English and can help my bad English!

Also you can just open issues, and I can look into them.

License
-------

The MIT License (MIT) Copyright (c) 2012 Hyeonje Jun.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
