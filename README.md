# About HRVInvestigator
HRVInvestigator is an interactive Dashboard Tool to explore ECG data. Its primary use is as a tool for the development of Seizure Detection Algorithms.

# How to use
There are 2 main ways to use HRVInvestigator:
## In IDE
Usage in the IDE has the advantage of sharing a kernel for better workflow integration.

use by opening HRVInvestigatorDashboard.ipynb in a separate window in your IDE

## in the browser

launch with (important to launch from inside the main directory)
```
 python -m panel serve HRVInvestigatorDashboard.ipynb
```

## Importing and Exporting Data
Data can be imported into the HRVInvestigator, by placing the Data inside the *DataArtifacts* Folder. Notably this also applies to the import inside the *Data Panel* which will fail otherwise. If HRVInvestigator is used in the *integrated mode* variables inside the same IPython kernel can also be loaded using the *Quick Import of the Processing Panel*
When exporting Data from HRVInvestigator, individual visulisation can either be saved using the controls on the visualisation itsef, or a dictionary represtentation using the *save data* button in the *data panel*. Using the save function dumps a dictionary of the same name as the object into the *DataArtifacts* folder and also stores the same information as a variable named *SavedData* in the IPython Kernel for quick access (if used in integrated mode).


# How to install

## with conda
```
conda create -n hrvinvestigator python=3.10
source activate hrvinvestigator
conda install -c conda-forge --file requirements.txt
```
## no install
or directly activate via the precompiled conda
```
source /path/to/conda/bin/activate path/to/project/HRVInvestigator2/conda_env2
```




# How to customise
HRVInvestigator has 2 main Axis of Extension, and allows the users to extend its processing capabilities by writing custom Processing and Evaluation Scripts.
All of these scripts share a common interface, using the *run* method, for execution and *set_vars* function to set internal variables necessary for computation. The must also *inherit from param.Parameterized* and their *class name must be equal to the file name*.
## Processing Scripts
Processing Scripts can be automatically recognised by HRVInvestigator if they are placed within the *Pipeline* folder. Using the previously defined syntax HRVInvestigator is also able provide and interface to set the variables inside the UI. For examples refer to **Pipeline/panThopkins.py**. HRVInvestigator will by default only supply the run function data attribute of the DataHistoryItem Object.

## ML Evaluation Scripts
In contrast to the Processing Scripts, the additional arguments of the Evaluation Scripts cannot at this time be provided by the UI. In contrast however, the run function is supplied by both, the entire *DataHistoryItem* object, and the name of the *pickled Model State Dictionary* meant to be stored in the *Models* subdirectory. For a simple example refer to **MLTransformation/sample.py**


# Code Structure and Further Extension
HRVInvestigator is made to be extended to better suit the needs of individual developers. As such the section below will provide an Overview of where to implement the desired changes, and to find the relevant code.
## HRVInvestigatorDashboard.ipynb
This file provides the central building Block of the program. It is structured by Panels, and is further structured inside those by visual blocks. After all blocks are created inside a panel, the blocks are assembled and orchestrated in the assembly section of each panel. All extension attempts are suggested start here.

## components 
A Library-like folder that holds commonly used functions an UI Elements of HRVInvestigator, referenced in the main Notebook.

## DataArtifacts
Place data here for Data Importing and Exporting

## HRVInvestigatorExtension
Defunct at the current time, this folder houses the building Blocks of the JupyterLab extension, that may at a later time provide 1-click access to the Dashboard.

## MLTransformation
Place MLEvaluation scripts here

## Pipeline
Place Processing Scripts here

## style
Adjust styling of the Dashboard in here. Be aware that generated HTML of panel is somewhat tricky to style and may require liberal use of the !important decorator.
