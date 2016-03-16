Jupyter notebook extensions
===========================

This repository contains a collection of extensions that add functionality to the Jupyter notebook.
These extensions are mostly written in Javascript and will be loaded locally in your Browser.

The IPython-contrib repository is maintained independently by a group of users and developers and not officially related
 to the IPython development team.

The maturity of the provided extensions may vary, please create an issue if you encounter any problems.


IPython/Jupyter version support
===============================

| Version     | Description                                                                                    |
|-------------|------------------------------------------------------------------------------------------------|
| IPython 1.x | not supported                                                                                  |
| IPython 2.x | [checkout 2.x branch](https://github.com/ipython-contrib/IPython-notebook-extensions/tree/2.x) |
| IPython 3.x | [checkout 3.x branch](https://github.com/ipython-contrib/IPython-notebook-extensions/tree/3.x) |
| Jupyter 4.x | [checkout master branch](https://github.com/ipython-contrib/IPython-notebook-extensions/)      |

There are different branches of the notebook extensions in this repository.
Please make sure you use the branch corresponding to your IPython/Jupyter version.


Documentation
=============

In the 4.x Jupyter repository, all extensions that are maintained and active have a markdown readme file for 
documentation and a yaml file to allow them being configured using the 'nbextensions' server extension.

![Extensions](nbextensions/config/icon.png)

For older releases (2.x and 3.x), and for general installation information, look at the [Wiki](https://github.com/ipython-contrib/IPython-notebook-extensions/wiki)

Some extensions are not documented. We encourage you to add documentation for them.


Installation
============

**pip-install**: As an experimental feature, it is now possible to install the collection of Jupyter extensions using pip, from the current master: 
Usage: enter
```
pip install https://github.com/ipython-contrib/IPython-notebook-extensions/archive/master.zip --user
```
- verbose mode can be enabled with -v switch eg pip -v install ...  
- upgrade with a --upgrade. 
- A system install can be done by omitting the --user switch.

After installation, simply go to the `/nbextensions/` page in the notebook to activate/deactivate  your notebook extensions.

Since this installation procedure is still experimental, please make an issue if needed. 

**install from a cloned repo**: 
You can clone the repo by 
```
git clone https://github.com/ipython-contrib/IPython-notebook-extensions.git
```
Then, if you want to install the extensions as local user, simply run `setup.py install`.

After installation, simply go to the `/nbextensions/` page in the notebook to activate/deactivate  your notebook extensions.

For more complex installation scenarios, please look up the documentation for installing notebook extensions, 
server extensions, pre/postprocessors, and templates at the Jupyter homepage http://www.jupyter.org

More information can also be found in the [Wiki](https://github.com/ipython-contrib/IPython-notebook-extensions/wiki)


setup.py
--------

This is the installation script that installs the notebook extensions for your local user.
It will
 1. find your local configuration directories
 2. install files from the following directories:
   * extensions - Python files like server extensions, pre- and postprocessors
   * nbextensions - notebook extensions, typically each extension has it's own directory
   * templates - jinja and html templates used by the extensions
 3. update nbconvert configuration (.py and .json) to load custom templates and pre-/postprocessors  
 4. update notebook configuration (.py and .json) to load server extensions, custom templates and pre-/postprocessors

**Important**: The installation script will overwrite files without asking. It will not delete files that do not belong
 to the repository. It will also not delete your Jupyter configuration.


Notebook extension structure
============================

Each notebook extension typically has it's own directory containing:
 * thisextension/main.js - javascript implementing the extension
 * thisextension/main.css - optional CSS
 * thisextension/readme.md- readme file describing the extension in markdown format
 * thisextension/config.yaml - file describing the extension to the nbconfig server extension

