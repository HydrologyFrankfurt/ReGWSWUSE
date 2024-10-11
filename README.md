# ReGWSWUSE
Reprogramming project of GWSWUSE, submodel of WaterGAP. 
# Branch description
This is the second major version of the project.
This version is configurable including cell-specific output.

In this version, it is not necessary to convert back to m3/year or m3/month in output_data_postprocessing, as all sector-specific results are calculated with input-unit.
The harmonisation of the units for the aggregation of the results across all sectors is carried out directly in the calc_cross_sector_totals() function.
