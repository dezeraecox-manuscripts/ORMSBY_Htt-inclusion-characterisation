# Collect pixels for both bleached and prebleached data - select "timepoints" folder

from ij import IJ, WindowManager, Prefs
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.gui import Roi, Toolbar, WaitForUserDialog
import os
from ij.io import DirectoryChooser, OpenDialog
from ij.process import ImageProcessor
from ij.plugin import ChannelSplitter

# define function to process each timepoint
def timepoint_processor(input_folder, impfile, folder):	
	# open image
	imp = IJ.openImage(os.path.join(input_folder, impfile))
	imp.show()
	impname = impfile.split(".")[0]
	pos_number = impname.split("_")[1]
	time_point = impname.split("_")[3]
	#	print impfile
	#	print pos_number
	#	print time_point

	# split channels into dictionary
	imps = ChannelSplitter.split(imp)
	imps_thresh = ChannelSplitter.split(imp)
	
	
	# define channel names list
	channel_names = ['FlAsH', 'mCherry']
	thresh_type = ["Li dark", "Yen dark"]
	
	# Show original channels, measure
	for x in range(0, len(channel_names)):
	
		print "Processing "+channel_names[x]+" channel"
		
		# define ROI manager
		rm = RoiManager.getInstance()
		if not rm:
	  		rm = RoiManager()
		rm.reset()
	
		# generate image to be measured
		imps[x].show()
		measure = imps[x].duplicate()
		print measure.title
		measure.show()
	
		# generate thresholded image for ROI
		imps_thresh[x].show()
		thresh = imps_thresh[x].duplicate()
		thresh.show()
		IJ.setAutoThreshold(thresh, thresh_type[x])
		IJ.run("Make Binary")
		IJ.run("Convert to Mask")
		
		# select thresholded image (to set ROIs)
		IJ.run("Set Measurements...", "area mean standard min area_fraction limit display add redirect=["+measure.title+" decimal=3")
		IJ.run("Analyze Particles...", "size=4-Infinity show=Outlines display clear add")
		
		# open background ROI
		back_roi = pos_number+'_backgroundROI.zip'
		rm.runCommand("Open", os.path.join(input_folder, back_roi))
	
		# get the results table and save
		rt1 = ResultsTable.getResultsTable()
		rt1.saveAs(os.path.join(folder, pos_number+"_"+time_point+"_ROI_"+channel_names[x]+"_Results.csv"))
	
		# get the ROI manager and save
		rm.runCommand("save selected", os.path.join(folder, pos_number+"_"+time_point+"_"+channel_names[x]+"_ROIs.zip"))
		
		print "Analyse particles completed for "+channel_names[x]
		
		# define new Results table
		rt = ResultsTable()
		
		IndRois = rm.getIndexes()
		for index in IndRois:
			ROI = rm.getRoi(index)
			ROI_name = ROI.getName()
			coords = ROI.getContainedPoints()
		
			row = 0
			for pixel in coords:
				x_coord = pixel.getX()
				y_coord = pixel.getY()
		
				rt.setValue(ROI_name+"_X_pos", row, int(x_coord))
				rt.setValue(ROI_name+"_Y_pos", row, int(y_coord))
			
				pixel_2 = imps[1].getProcessor().getPixel(int(x_coord), int(y_coord))
				rt.setValue(ROI_name+"_"+channel_names[1], row, pixel_2)
		
		  		row = row + 1
		rt.show("Results")
		
		rt.save(os.path.join(folder, pos_number+"_"+time_point+'_'+channel_names[x]+"_pixels.csv"))
		print "Pixel collection done!"

	print("Process Complete")
	print("Results for "+pos_number+" saved in directory: "+folder)

	close_images()
	

def close_images():
	open_images = WindowManager.getImageTitles()
	for imagename in open_images:
		print imagename
		IJ.selectWindow(imagename)
		IJ.run("Close")
	print "Windows closed"

##-----------------Adjust inputs here---------------------------------
# get input path for merge file
opener = DirectoryChooser("Select the input folder")
input_folder = opener.getDirectory()

#Define results output folder
folder = input_folder+"Results_/"
if not os.path.exists(folder):
	os.mkdir(folder)
# collect list of files to be processed
file_list = [filename for filename in os.listdir(input_folder) if ".tif" in filename]

print file_list

# process each file
for filename in file_list:
	print "Processing timepoint "+filename
	timepoint_processor(input_folder, filename, folder)

print "Process complete!"	
		
