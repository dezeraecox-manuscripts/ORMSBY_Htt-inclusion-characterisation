from ij import IJ, WindowManager, Prefs
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.gui import Roi, Toolbar, WaitForUserDialog, PolygonRoi
import os
from ij.io import DirectoryChooser, OpenDialog
from ij.process import ImageProcessor
from ij.plugin import RoiEnlarger

opener = DirectoryChooser("Select the input folder")
input_folder = opener.getDirectory()

image_names = []
for filename in os.listdir(input_folder):
    print filename
    if filename.split(".")[-1] == "tif":
    	image_names.append(filename)
print image_names

#Define results output folder
output_folder = input_folder+"Results/"
if not os.path.exists(output_folder):
	os.mkdir(output_folder)

def image_processing(impfile, input_folder, output_folder):
	# open image
	imp = IJ.openImage(os.path.join(input_folder, impfile))
	imp.show()
	channel_pos = impfile.split(".")[0]
	pos = channel_pos.split("_")[3]
	ROIset_name = "RoiSet_Pos"+pos+'.zip'
	print input_folder
	print channel_pos
	print pos
	print os.path.join(input_folder, ROIset_name)
	
	#open saved ROI files?
	rm = RoiManager()
	rm.runCommand("Open", os.path.join(input_folder, ROIset_name))
	
	# define a results table
	#rt = ResultsTable.getResultsTable()
	
	# Add in ROI elements here
	# get a list of the indexes of available (or selected if some selected) ROIs
	rt = ResultsTable()
	
	# define a results table
	#rt2 = ResultsTable.getResultsTable()
	
	# Add in ROI elements here
	# get a list of the indexes of available (or selected if some selected) ROIs
	rt2 = ResultsTable()
	
	
	IndRois = rm.getIndexes()
	row_manager = 0
	for index in IndRois:
		ROI = rm.getRoi(index)
		ROI_name = ROI.getName()
		ROI_shrinked = RoiEnlarger.enlarge(ROI, -1)
	
		# Actual ROI
		ROI_coords = ROI.getContainedPoints()
		row = 0
		for pixel in ROI_coords:
			x_coord = pixel.getX()
			y_coord = pixel.getY()
	#		pixel = imp1.getProcessor().getPixel(int(x_coord), int(y_coord))
			rt.setValue(ROI_name+"_X_pos", row, int(x_coord))
			rt.setValue(ROI_name+"_Y_pos", row, int(y_coord))
	  		row = row + 1
	
		# Shrunken ROI
	  	shrunk_coords = ROI_shrinked.getContainedPoints()
	  	row = 0
		for pixel in shrunk_coords:
			x_coord = pixel.getX()
			y_coord = pixel.getY()
	#		pixel = imp1.getProcessor().getPixel(int(x_coord), int(y_coord))
			rt.setValue(ROI_name+"_X_pos_s", row, int(x_coord))
			rt.setValue(ROI_name+"_Y_pos_s", row, int(y_coord))
	  		row = row + 1
	
	  	# Add centroids to another results table
	  	centre_pos = ROI.getContourCentroid()
	  	rt2.setValue("ROI_name", row_manager, ROI_name)
	  	rt2.setValue("Centroid_X_pos", row_manager, int(centre_pos[0]))
		rt2.setValue("Centroid_Y_pos", row_manager, int(centre_pos[1]))
	  	row_manager = row_manager + 1
	  	
	rt.show("Coords")
	rt.save(os.path.join(output_folder, channel_pos+"_pixel_cords.csv"))
	
	rt2.show("Centroids")
	rt2.save(os.path.join(output_folder, channel_pos+"_centroids.csv"))
	
	print("Process Complete for "+pos+" ROIs")
	print("Results for "+channel_pos+" saved in directory: "+output_folder)

	# Close all windows
	IJ.selectWindow("Coords")
	IJ.run("Close")
	IJ.selectWindow("Centroids")
	IJ.run("Close")
	rm.close()
	imp.close()
	

for impfile in image_names:
	image_processing(impfile, input_folder, output_folder)
	print "Processing complete."