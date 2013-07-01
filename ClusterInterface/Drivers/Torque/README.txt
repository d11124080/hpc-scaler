+---------------------------------------------+
|   Drivers folder for Cluster Interface      |
+---------------------------------------------+
| This folder contains individual 'vendor-    |
| specific' drivers which allow the Cluster   |
| Interface to be integrated into a wider     |
| variety of Cluster Architectures.           |
|                                             |
| Each driver should be created within a      |
| folder which corresponds to the driver name.|
| Within this folder there must be a Python   |
| module with the corresponding name which    |
| serves as a constructor for the driver.     |
|                                             |
| Third party software, such as open source   |
| libraries or proprietary vendor-provided    |
| tools, should be placed within a further    |
| subdirectory of the driver. This is for the |
| purposes of maintaining the modularity and  |
| heterogenity of the Cluster Interface.      |
+---------------------------------------------+