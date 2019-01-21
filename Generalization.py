# -*- coding: latin_1 -*-
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:        AutokastBatch.py
# Purpose:     Implementation of the AutoKAST algorithm in ArcPy for NVE
#
# Author:      Haavard Toft Larsen
#
# Created:     03.10.2018
# Licence:     Copyright
# ------------------------------------------------------------------------------------------------------------------------------------------------------


# --- Import modules
import os
import arcpy
import traceback
import sys
from arcpy import *
from arcpy.sa import *

env.overwriteOutput = True

# --- Set Working Directory
env.workspace = r"\\nve.no\fil\home\htla\Dokumenter\ArcGIS\TestFolder\Autokast.gdb"
rasterfolder = r"\\nve.no\fil\home\htla\Dokumenter\ArcGIS\TestFolder\Raster_Files"

FID = arcpy.GetParameterAsText(0)

# --- Set Input Files
Autokast = r"\\nve.no\fil\home\htla\Dokumenter\ArcGIS\Default.gdb\Large_Norge_FID0_Merge"
# HAV = r"\\nve.no\fil\home\htla\Skrivebord\Grunnfiler\Landmaske.shp"

# --- The area of interest that is going to be generalized
Outline = r"\\nve.no\fil\home\htla\Dokumenter\ArcGIS\Default.gdb\Landmaske_Clip"

# --- Set Output File Names
# Autokast_123 = r"\\nve.no\fil\home\htla\Skrivebord\Grunnfiler\Generalisert\Autokast_gen.tif"
Output = r"\\nve.no\fil\home\htla\Skrivebord\Grunnfiler\Autokast_%s.tif" %FID

arcpy.CheckOutExtension("Spatial")

arcpy.env.snapRaster = Autokast

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# --- Make Feature Layer
arcpy.MakeFeatureLayer_management(in_features=Outline, out_layer="VassOmr_Layer", where_clause="FID =%s" %FID, workspace="", field_info="OBJECTID OBJECTID VISIBLE NONE;Shape Shape VISIBLE NONE;FID_LandmaskeFID2_Union FID_LandmaskeFID2_Union VISIBLE NONE;FID_LandmaskeFID2 FID_LandmaskeFID2 VISIBLE NONE;Name Name VISIBLE NONE;FID_LandmaskeFID1 FID_LandmaskeFID1 VISIBLE NONE;Name_1 Name_1 VISIBLE NONE;FID_LandmaskeFID3 FID_LandmaskeFID3 VISIBLE NONE;Name_12 Name_12 VISIBLE NONE;Shape_Length Shape_Length VISIBLE NONE;Shape_Area Shape_Area VISIBLE NONE;FID FID VISIBLE NONE")
arcpy.CopyFeatures_management("vassOmr_Layer", os.path.join(rasterfolder, "Outline.shp"));

print("Outline created")

# --- Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# --- Clip out an area to be smoothed
arcpy.Clip_analysis(in_features=Autokast, clip_features=os.path.join(rasterfolder, "Outline.shp"), out_feature_class="Autokast_Polygon", cluster_tolerance="")

print("Clip completed")

# ----------------------------------------------------------------------------------------------------------------------

arcpy.PolygonToRaster_conversion(in_features="Autokast_Polygon", value_field="Class", out_rasterdataset=os.path.join(rasterfolder, "Raster.tif"), cell_assignment="CELL_CENTER", priority_field="NONE", cellsize="10")

print("Polygon To Raster")

arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "Raster.tif"), "Value", "1 1;2 2;3 3;NODATA 1", os.path.join(rasterfolder, "Raster123.tif"), "DATA")

arcpy.gp.ExtractByMask_sa(os.path.join(rasterfolder, "Raster123.tif"), os.path.join(rasterfolder, "Outline.shp"), os.path.join(rasterfolder, "Raster123_Extract.tif"))

# --- Raster to polygon (need to be feature type to use the function smooth)
arcpy.RasterToPolygon_conversion(os.path.join(rasterfolder, "Raster123_Extract.tif"), "Autokast_Polygon", simplify="NO_SIMPLIFY", raster_field="Value")

print("Raster to Feature type complete")

# ----------------------------------------------------------------------------------------------------------------------

# --- Smooth polygons
arcpy.SmoothPolygon_cartography(in_features="Autokast_Polygon", out_feature_class="Autokast_Smooth", algorithm="PAEK", tolerance="500 Meters", endpoint_option="FIXED_ENDPOINT", error_option="NO_CHECK")

print("Smoothed")

# --- Dissolve
arcpy.Dissolve_management(in_features="Autokast_Smooth", out_feature_class="Autokast_Dissolve", dissolve_field="gridcode", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

print("Dissolved")

# Eliminate polygons smaller than 25000 square meters
arcpy.EliminatePolygonPart_management(in_features="Autokast_Dissolve", out_feature_class="Autokast_Smooth_Eliminate", condition="AREA", part_area="25000 SquareMeters", part_area_percent="0", part_option="ANY")

print("Eliminate clusters completed")

# Convert the file back to raster
arcpy.PolygonToRaster_conversion(in_features="Autokast_Smooth_Eliminate", value_field="gridcode", out_rasterdataset=os.path.join(rasterfolder, "AutokastToRaster.tif"), cell_assignment="CELL_CENTER", priority_field="NONE", cellsize="10")

print("Converted back to raster")

# Expand cells to remove holes from the smooth tool
arcpy.gp.Expand_sa(os.path.join(rasterfolder, "AutokastToRaster.tif"), os.path.join(rasterfolder, "Autokast_Expand.tif"), "25", "1;2;3")

print ("Cells expanded")

# --- Extract by mask
outExtractByMask = ExtractByMask(os.path.join(rasterfolder, "Autokast_Expand.tif"), os.path.join(rasterfolder, "Outline.shp"))
outExtractByMask.save(Output)

print("Completed")
