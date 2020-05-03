from ij import IJ, WindowManager, Prefs
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.gui import Roi, Toolbar, WaitForUserDialog
import os
from ij.io import DirectoryChooser, OpenDialog
from ij.process import ImageProcessor
from array import array


# get input path for merge file
opener = OpenDialog("Select the merge image")
input_folder = opener.getDirectory()
impfile = opener.getFileName()

#Define results output folder
folder = input_folder+"Results/"

if not os.path.exists(folder):
	os.mkdir(folder)

# open image
imp = IJ.openImage(os.path.join(input_folder, impfile))
imp.show()
name_kinda = impfile.split(".")[2]
##print name_kinda
impname = name_kinda.split(" ")[2]
#print impfile
#print impname

# define a results table
rt = ResultsTable()

# Stack to images
IJ.run("Stack to Images")


# Duplicate windows with appropriate channel name (select the image for ROI definition LAST)
channel_1_name = "c:1/8 - "+impname
#print channel_1_name
channel_2_name = "c:3/8 - "+impname
#print channel_2_name
channel_3_name = "c:7/8 - "+impname
#print channel_3_name
channel_4_name = "c:8/8 - "+impname
#print channel_4_name

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_1_name))
IJ.run("Duplicate...", "title=channel_1")
IJ.run("32-bit")
IJ.run("Cyan")

# Set to appropriate windows
WindowManager.setCurrentWindow(WindowManager.getWindow(channel_2_name))
IJ.run("Duplicate...", "title=channel_2")
IJ.run("32-bit")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_3_name))
IJ.run("Duplicate...", "title=channel_3")
IJ.run("32-bit")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_4_name))
IJ.run("Duplicate...", "title=channel_4")
IJ.run("32-bit")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_4_name))
IJ.run("Duplicate...", "title=channel_5")
IJ.run("32-bit")
IJ.run("Red")

IJ.run("Add Image...", "image=["+channel_1_name+"] x=0 y=0 opacity=60")


# Get ROI manager instance, save to zip
rm = RoiManager.getInstance()
if not rm:
  rm = RoiManager()
rm.reset()

# select X channel (to set ROIs)
# Wait for user to add ROIs to manager
Prefs.multiPointMode = True
pause = WaitForUserDialog("Select ROIs of interest and add to manager \n \nPress OK to continue")
pause.show()

rm.runCommand("save selected", os.path.join(folder, impname+"_ROIs.zip"))

# select the ROIs listed in the array
positions = rm.getRoisAsArray()

# Set meaurements to Y channel, save results table and clear
#IJ.run("Set Measurements...", "area mean standard min limit display redirect=[channel_1] add decimal=3")
WindowManager.setCurrentWindow(WindowManager.getWindow(channel_1_name))
channel_1_process = IJ.getProcessor()

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_2_name))
channel_2_process = IJ.getProcessor()

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_3_name))
channel_3_process = IJ.getProcessor()

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_4_name))
channel_4_process = IJ.getProcessor()


IndRois = rm.getIndexes()
row = 0
for index in IndRois:

	ROI = rm.getRoi(index)
	ROI_name = ROI.getName()

	
	channel_1_process.setRoi(ROI)
	c1_intensity = channel_1_process.getStatistics()

	channel_2_process.setRoi(ROI)
	c2_intensity = channel_2_process.getStatistics()

	channel_3_process.setRoi(ROI)
	c3_intensity = channel_3_process.getStatistics()

	channel_4_process.setRoi(ROI)
	c4_intensity = channel_4_process.getStatistics()

	rt.setValue("ROI", row, ROI_name)
	
	rt.setValue("c1_intensity", row, c1_intensity.mean)
	rt.setValue("c2_intensity", row, c2_intensity.mean)
	rt.setValue("c3_intensity", row, c3_intensity.mean)
	rt.setValue("c4_intensity", row, c4_intensity.mean)
	
	rt.addResults()

	row += 1

# Get results table and save
rt.saveAs(os.path.join(folder, impname+"_Results.csv"))


print "Done"