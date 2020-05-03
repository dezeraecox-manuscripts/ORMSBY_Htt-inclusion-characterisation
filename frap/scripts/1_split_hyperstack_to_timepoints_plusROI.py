# Collect background ROIs for both bleached and prebleached data - generates individual timepoints folder


from ij import IJ, WindowManager, Prefs
from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.gui import Roi, Toolbar, WaitForUserDialog
import os
from ij.io import DirectoryChooser, OpenDialog
from ij.process import ImageProcessor
from ij.plugin import ChannelSplitter

# Bioformats
from loci.plugins import BF
from loci.common import Region
from loci.plugins.in import ImporterOptions

# define ROI background function
def ROI_background(input_folder, impfile, folder):
	# read in and display ImagePlus(es) with arguments
	options = ImporterOptions()
	options.setId(input_folder+impfile)
	imps = BF.openImagePlus(options)

	# open original hyperstack
	for imp in imps:
	    imp.show()
	rm = RoiManager.getInstance()
	if not rm:
			rm = RoiManager()
	rm.reset()
	# this is the method to wait for user input
	WaitForUserDialog("Background","Select and add a background ROI").show()
	pos_name = impfile.split("_")[1]
	pos = pos_name.split(".")[0]
	rm.runCommand("save selected", os.path.join(folder, pos+"_backgroundROI.zip"))
	print "Background ROI saved for position "+pos

# Define hyperstack splitting function
def hyperstack_splitter(input_folder, impfile, folder):
	# Open hyperstack using bioformats, sith split timepoints
	options = ImporterOptions()
	options.setId(input_folder+impfile)
	options.setSplitTimepoints(True)
	imps = BF.openImagePlus(options)
	# save each individual channel stack
	for imp in imps:
	    imp.show()
	    name = imp.getTitle()
	    almost_pos = name.split("_")[1]
	    pos = almost_pos.split(".")[0]
	    time = name.split("=")[1]
#	    print name
#	    print pos
#	    print time
	    new_name = "pos_"+pos+"_t_"+time
	    IJ.saveAs(imp, "Tiff", os.path.join(folder, new_name))
	    imp.close()
	print "Done splitting hyperstack for "+pos

# get input path from selected file file
opener = DirectoryChooser("Select the input folder")
input_folder = opener.getDirectory()
#print input_folder

#Define results output folder
folder = input_folder+"timepoints/"
if not os.path.exists(folder):
	os.mkdir(folder)

file_list = [filename for filename in os.listdir(input_folder) if ".tif" in filename]

print file_list

for filename in file_list:
	print "Collecting background ROI for "+filename
	ROI_background(input_folder, filename, folder)
	print "Splitting hyperstacks for "+filename
	hyperstack_splitter(input_folder, filename, folder)

print "Process complete!"	
