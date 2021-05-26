---
title:  "Moving window operations across arrays"
author: Dr Chris Williams
categories:
  - data analytics
  - geospatial analysis
tags:
  - Python
  - R
  - Data Analysis
  - Data Processing
  - Geospatial
 ---

Applying functions using moving windows are a common feature of geospatial data analysis and often exist "under the hood" of GIS software. If you've ever calculated a slope or aspect grid from a raster elevation dataset, then the program you've used has made use of a moving window processing operation. This is particularly relevant for the processing of raster datasets.

Often, an analyst may find that they need to fine tune or create the specific function that will be used by the processing kernel (or across the cells that a moving window covers). Having a quick and efficient way to do this makes it not only possible to apply any function you want across a dataset, but also to consider impacts of scale etc. The below example shows a simple case of doing this with python's `numpy` and `scipy` modules. For those working in R, you should have a look at the `focal` function in the [raster package](https://cran.r-project.org/web/packages/raster/index.html).

## Numpy example 

Using a simple numpy example:

```python
import numpy as np
from scipy import ndimage

# Define a function that you want to run within the moving window 
# that will operate in a neighbourhood around each cell of the array
# to process
# Making this "cell" independent (by avoiding functions that depend 
# on specific cell positions within the window) will make the function
# much more scalable
def focal_variance(subarr):
	"""Calcualte variance of an array
	"""
	return(ndimage.variance(subarr))

# Create an array to process
arr = np.array([[1, 2, 0, 0],
		[5, 3, 0, 4],
		[0, 0, 0, 7],
		[9, 3, 0, 0]])

# Define dimensions of moving window
k=3
footprint=np.ones((k,k))

# Apply moving window across array
ndimage.generic_filter(arr, focal_variance, footprint=footprint)
```

The same approach then can then be applied across a geosptial raster tile such as a geotiff. The steps being:

1. read in raster dataset such as with gdal
2. get hold of the array of values
3. setup your moving window dimensions - this is just the shape of your filter (the values don't matter, just the shape)
4. define some function to use across the array - something that operates over an array and returns one value
	- this function will be run at each element of an input array, with the result of the function being used 
		to populate the same element of an output array - an example function:
5. Use scipy's ndimage.gerenic _filter() to apply the function across the array within the defined moving window / kernel
6. The output of ndimage.generic_filter will be an array of the same size as your input - write this to a geotiff with the same geospatial information as the input array 
	- note that this assumes it's the same size - otherwise you need to recalculate this information

The below code expands on the numpy example, using gdal to read in and write out the data values.

## Geospatial example

```python
import sys
import numpy as np
from scipy import ndimage
from osgeo import gdal
from osgeo.gdalconst import *

#Setup variables
INPUT_DATA="your_input.tif"
OFILE="your_output.tif"
KERNEL_DIMENSIONS=[3,3] # doesn't have to be square

#Read in with gdal
inDs = gdal.Open(INPUT_DATA)

#Get data and geotransform info
geotransform = inDs.GetGeoTransform()
rows = inDs.RasterYSize
cols = inDs.RasterXSize
array2process = np.array(inDs.ReadAsArray())

#Sort array in case of NAN values
workarr = np.nan_to_num(array2process)

#Set up function 
def focal_variance(subarr):
	"""Calcualte variance of an array
	"""
	return(ndimage.variance(subarr))

#Set up moving window (kernel) dimensions
footprint=np.ones((KERNEL_DIMENSIONS[0],KERNEL_DIMENSIONS[1])) 

#Apply function across dataset
processedArray=ndimage.generic_filter(workarr, focal_variance, footprint=footprint)

#~~~~~~~~~~~~~~~~~
#Write out dataset, assigning geotransform info of the input dataset
# - assumes that output array has the same dimensions as the input array

#Create the output gdal object
driver = inDs.GetDriver()

outDs = driver.Create(OFILE, cols, rows, 1, GDT_Float32)
if outDs is None:
    sys.exit("Unable to create %s" %OFILE)

outBand = outDs.GetRasterBand(1)

# write the data
outBand.WriteArray(processedArray)

# georeference the data and set the projection based on input dataset
outDs.SetGeoTransform(inDs.GetGeoTransform())
outDs.SetProjection(inDs.GetProjection())
outBand.SetNoDataValue(np.nan)

outBand.FlushCache()
```
