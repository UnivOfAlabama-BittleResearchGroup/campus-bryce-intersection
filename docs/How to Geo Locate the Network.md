# How to Geo-Locate a SUMO Network

### 1. Understanding the location information in the *.net.xml file

At the top of the .net.xml file, there is an xml element that looks like either:

``<location netOffset="0.00,0.00" convBoundary="-355.14,-1108.16,393.23,944.28" origBoundary="-10000000000.00,-10000000000.00,10000000000.00,10000000000.00" projParameter="!"/>``

or in a geo-located network:

``<location netOffset="-448796,-3665419" convBoundary="-355.14,-1108.16,393.23,944.28" origBoundary="-87.549070,33.126330,-87.54478,33.13464" projParameter="+proj=utm +zone=16 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>``
 
#### variable: ``netOffset``
- the location of (0,0) point in the network. 
- in an osmWebWizard generated network, this is likely the bottom-left most node. A user-generated network is likely to have the (0,0) point at an arbitrary location
- the values used for the netOffset depend on the ``projParam`` used
- **when a network is geo-located, the vales for the ``netOffset`` are -1 x Easting and -1 x Northing values in meters for 
the real-life location of the (0,0) point**

#### variable: ``convBoundary``
- the boundary in meters that surrounds the network: (x_min, y_min, x_max, y_max)
- these values should be auto-populated by NETEDIT (you do not need to touch)
 
#### variable: ``origBoundary``
- if the network is geo-located, these values are the GPS coordinates of the ``convBoundary``
- They are given as (longitude of x_min, latitude of y_min, longitude of x_max, latitude of y_max) 
 
#### variable: ``projParameter``
- information specifying how the projection should be made. 

### 2. How to locate the network
 
#### Step 1.

use osmWebWizard to generate a network in a similar location as the network that you wish to geo-locate. (This will give 
you the correct projection parameter info)

#### Step 2.

open the osmWebWizard net file and copy the ``projParameter`` information.

replace the ``projParameter`` information in your net file with the copied information.

### Step 3.

place POIs in your desired network at the following points: (0,0), (x_min, y_min), (x_max, y_max)

POIs are added to the network inside of NetEdit by clicking on the red pyramid and then selecting the "poi" shape element.  

### Step 4.

use a tool like https://www.geoplaner.com/ to find find the GPS coordinates of the 3 points in step 3
- this can be a bit of a guessing game. It helps if you have a decal file or image of the network in the 
background of NETEDIT to help with the location.

### Step 5.

once the 3 points have been located, the information can be added the the *.net.xml file like so:

``<location netOffset="-1*Easting@(0,0),-1*Northing@(0,0)" convBoundary="(x_min, y_min, x_max, y_max)" 
origBoundary="longitude@(x_min, y_min),latitude@(x_min, y_min),longitude@(x_max, y_max),latitude@(x_max, y_max)" 
projParameter="+proj=utm +zone=16 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>``

### Step 6.

Check that the POI location information matches the real-life locations.

Check random points in the network by right-clicking and copying the cursor geo-position

If all-good, the network is now geo-located!

### Step 7. 

Use the following to generate a background image:

`` python %SUMO_HOME%\tools\tileGet.py -n <net-file-path> -t 10 ``

SUMO has more documentation on the tileGet tool here: https://sumo.dlr.de/docs/Tools/Misc.html#tilegetpy

### Step 8.

move the "settings.xml" and the image files to your desired location. They can be loaded into NetEdit by selecting the color wheel and then in the "Background" tab clicking the "Load Decals" button and selecting your settings file. 
