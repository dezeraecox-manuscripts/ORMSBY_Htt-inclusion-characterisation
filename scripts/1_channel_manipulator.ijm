//This macro batch processes all the files in a folder and any
// subfolders in that folder. For only red or green images, comment
//out the appropriate sections in the last function

// initialises all functions (count files, process files)
dir = getDirectory("Choose a Directory ");
setBatchMode(true);
count = 0;
countFiles(dir);
n = 0;
processFiles(dir);
print(count+" files processed");
print("Done");

//produces a list of all files in the directory   
function countFiles(dir) {
   list = getFileList(dir);
   for (i=0; i<list.length; i++) {
       if (endsWith(list[i], "/"))
           countFiles(""+dir+list[i]);
       else
           count++;
   }
}


//processes all files in both current directory and subfolders
function processFiles(dir) {
   list = getFileList(dir);
   for (i=0; i<list.length; i++) {
       showProgress(n++, count);
       path = dir+list[i];
       processFile(path);
       }
   }


//applies the relevant actions to each file
function processFile(path) {
    if (endsWith(path, ".tif")) {
        open(path);
        imageTitle=getTitle();//returns a string with the image title
        imageSorter(imageTitle); 
    	
   }

function imageSorter(imageTitle){

		outputDir = getDirectory("image") + "/Results/";
		run("Stack to Images");
		newTitle= split(imageTitle, "-");
		//print(imageTitle);
		//print(newTitle[0]);
		//print(newTitle[1] + "-" + newTitle[2]);
		newimageTitle = newTitle[1] + "-" + newTitle[2];
		//print(newimageTitle);
		finalTitle= split(newimageTitle, ".");
		//print(finalTitle[0]);

		//collecting variables for each channel

		//collecting variables for each channel

		Cer_incl= "c:1/8 -"+finalTitle[0];
		RNA_incl= "c:3/8 -"+finalTitle[0];
		Hoechst= "c:4/8 -"+finalTitle[0];
		Cer_cyto= "c:5/8 -"+finalTitle[0];
		FlAsH_cyto="c:6/8 -"+finalTitle[0];
		FlAsH_incl= "c:7/8 -"+finalTitle[0];
		RNA_cyto= "c:8/8 -"+finalTitle[0];

		//Cer
		selectWindow(Cer_incl); 
		run("Cyan");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C1-"+imageTitle);
		close();


		//RNA_incl
		selectWindow(RNA_incl); 
		run("Red");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C3-"+imageTitle);
		close();

		//Hoechst
		selectWindow(Hoechst); 
		run("Magenta");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C4-"+imageTitle);
		close();

		//Cer_cyto
		selectWindow(Cer_cyto); 
		run("Cyan");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C5-"+imageTitle);
		close();

		//FlAsH_incl
		selectWindow(FlAsH_incl); 
		run("Green");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C6-"+imageTitle);
		close();

		//FlAsH_cyto
		selectWindow(FlAsH_cyto); 
		run("Green");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C7-"+imageTitle);
		close();

		//RNA_cyto
		selectWindow(RNA_cyto); 
		run("Red");
		//setMinAndMax(0, 65000);
		run("Duplicate...", "title");
		saveAs("Tiff", outputDir+"C8-"+imageTitle);
		close();

		//Cer_incl
		selectWindow(Cer_incl); 
		//run("Red");
		//setMinAndMax(0, 65000);
		//run("Duplicate...", "title");
	
		saveAs("Tiff", outputDir+imageTitle);
		close();
		

		
     	while (nImages>0) { 
          selectImage(nImages); 
          close();

}
}
}
