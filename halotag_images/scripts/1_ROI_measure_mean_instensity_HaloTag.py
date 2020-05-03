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
impfile

#Define results output folder
folder = input_folder+"Results/"

if not os.path.exists(folder):
	os.mkdir(folder)

impfile = impfile.split("-")[1]
#print impfile

# define a results table
rt = ResultsTable()


# Duplicate windows with appropriate channel name (select the image for ROI definition LAST)
channel_1_name = "C1-"+impfile
C1 = IJ.openImage(os.path.join(input_folder, channel_1_name))
C1.show()
channel_2_name = "C2-"+impfile
C2 = IJ.openImage(os.path.join(input_folder, channel_2_name))
C2.show()
channel_3_name = "C3-"+impfile
C3 = IJ.openImage(os.path.join(input_folder, channel_3_name))
C3.show()
channel_4_name = "C4-"+impfile
C4 = IJ.openImage(os.path.join(input_folder, channel_4_name))
C4.show()
channel_5_name = "C5-"+impfile
C5 = IJ.openImage(os.path.join(input_folder, channel_5_name))
C5.show()

# Set to appropriate windows
WindowManager.setCurrentWindow(WindowManager.getWindow(channel_1_name))
IJ.run("Duplicate...", "title=channel_1")
IJ.run("32-bit")
IJ.run("Cyan")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_2_name))
IJ.run("Duplicate...", "title=channel_2")
IJ.run("32-bit")
IJ.run("Grays")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_3_name))
IJ.run("Duplicate...", "title=channel_3")
IJ.run("32-bit")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_4_name))
IJ.run("Duplicate...", "title=channel_5")
IJ.run("32-bit")

#WindowManager.setCurrentWindow(WindowManager.getWindow(channel_5_name))
#IJ.run("Duplicate...", "title=channel_4")
#IJ.run("32-bit")
#IJ.run("Red")

IJ.run("Add Image...", "image=[channel_1] x=0 y=0 opacity=80")
IJ.run("Add Image...", "image=[channel_2] x=0 y=0 opacity=60")

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_5_name))
IJ.run("Duplicate...", "title=channel_4")
IJ.run("32-bit")
IJ.run("Red")


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

rm.runCommand("save selected", os.path.join(folder, impfile+"_ROIs.zip"))

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

WindowManager.setCurrentWindow(WindowManager.getWindow(channel_5_name))
channel_5_process = IJ.getProcessor()


IndRois = rm.getIndexes()
row = 0
for index in IndRois:

	ROI = rm.getRoi(index)
	ROI_name = ROI.getName()

	
	channel_1_process.setRoi(ROI)
	c1_intensity = channel_1_process.getStatistics()

	#channel_2_process.setRoi(ROI)
	#c2_intensity = channel_2_process.getStatistics()

	channel_3_process.setRoi(ROI)
	c3_intensity = channel_3_process.getStatistics()

	channel_4_process.setRoi(ROI)
	c4_intensity = channel_4_process.getStatistics()

	channel_5_process.setRoi(ROI)
	c5_intensity = channel_5_process.getStatistics()

	rt.setValue("ROI", row, ROI_name)
	
	rt.setValue("c1_intensity", row, c1_intensity.mean)
	#rt.setValue("c2_intensity", row, c2_intensity.mean)
	rt.setValue("c3_intensity", row, c3_intensity.mean)
	rt.setValue("c4_intensity", row, c4_intensity.mean)
	rt.setValue("c5_intensity", row, c5_intensity.mean)
	
	rt.addResults()

	row += 1

# Get results table and save
rt.saveAs(os.path.join(folder, impfile+"_Results.csv"))


print "Done"