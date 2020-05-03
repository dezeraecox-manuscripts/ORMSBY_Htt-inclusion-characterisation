# ORMSBY_Htt inclusion characterisation

This repo contains the code and example data associated with the HBRi/PBRi characterisation project, led by Angelique Ormsby. This manuscript has been submitted for publication.

Manuscript preprint: [link]

Final version: _upon acceptance_

## Prerequisites

This analysis assumes a standard installation of [Python 3](https://www.python.org/downloads/) (=> 3.6) and [FiJi](https://fiji.sc/) (v 2.0.0) <sup>[1](footnote_1)</sup>. For specific package requirements, see the `environment.yml` file.


## Workflow

Example raw images and partially processed results are provided here to test the included analysis scripts. 

Initial preprocessing of the raw files to extract `TIFF` images from proprietary formats was completed in ImageJ, using the Bioformats importer (available via the drag-and-drop interface). Stacked or individual `TIFF` files were then exported for further processing where necessary.

1. Click-It and HaloTag images

| Script                        | Language/Interpreter  | Description                        |
|-------------------------------|-----------------------|------------------------------------|
|ROI_measure_mean_intensity     | Jython/ImageJ         | Define ROIs, collect per-pixel information and calculate mean intensity |
|ROI_analysis_concatenator      | Python                | Collect ROIs and calculate mean FlAsH/Cerulean fluorescence |

2. Halotag flow cytometry

    *NB: Example raw data is preanalysed with flowjo, such that cells in "i" and "ni" gates are exported to individual `.csv` files.*

| Script         | Language/Interpreter | Description |
|--------        |----------------------|-------------|
|Initial_cleanup | Python               | Collect original per-cell data from fcs exports, label with inclusion identity |
|Calculate_inclusions | Python          | Assign cerulean and halotag fluorescence to bins, then calculate percentage of cells in each bin assigned to inclusion gate |
|Plotting        | Python               | Generate overall and per-bin plots for inclusion-containing cells |


3. FRAP images

| Script | Language/Interpreter | Description  |
|--------|----------------------|--------------|
| split_hyperstack_to_timepoints_plusROI | Jython/ImageJ    | Collect background ROI and split hyperstack into individual TIFF timepoints |                                               |
| ROI_pixel_collector | Jython/ImageJ | Apply automatic thresholding to pre/bleached ROIs and collect pixel to calculate mean intensity |
| Pixel_calculator | Python | Match ROIs across timepoints and calculate bleached ROI using pixel coordinates. Calculate background-corrected FRAP value |


4. Antibody penetration

| Script        | Language/Interpreter | Description |
|---------------|----------------------|-------------|
|ROI_centroids  | Jython/ImageJ        | Using predefined ROIs, collect pixels and centroids for outer (inclusion) and inner (antibody penetration) ROI |
|Euclidean_distance_calculator | Python | Collect boundary pixels for each ROI and calculate mean euclidean distance from centroid |


## References

<a name="footnote_1">1.</a> Schindelin, J.; Arganda-Carreras, I. & Frise, E. et al. (2012), "Fiji: an open-source platform for biological-image analysis", Nature methods 9(7): 676-682, PMID 22743772, doi:10.1038/nmeth.2019 (on Google Scholar).

