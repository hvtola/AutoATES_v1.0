# -*- coding: latin_1 -*-
# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Name:        AutokastBatch.py
# Purpose:     Implementation of the AutoKAST algorithm in ArcPy for NVE
#
# Author:      Håvard Toft Larsen
#
# Created:     15.05.2018
# Modified:    22.11.2018
# Licence:     GNU General Public License version 3, 2007
# ------------------------------------------------------------------------------------------------------------------------------------------------------


# --- Import arcpy module
import arcpy
import os
import sys
import traceback
import glob
import time
from arcpy.sa import *

arcpy.env.overwriteOutput = True

# --- Path to LogFile
LogFile = r"\\nve.no\fil\home\htla\Dokumenter\ArcGIS\Raster_Files\Autokast.log"

# --- Set Working Directory
arcpy.env.workspace = r"C:\AutokastFiles\16.01.19\Feature_Files.gdb"
rasterfolder = r"C:\AutokastFiles\16.01.19\Raster_Files"

# --- Set Input Files
DEM = r"\\nve.no\fil\gis i nve\DTM10\DTM10.gdb\DTM10"
Outline = r"\\nve.no\fil\home\htla\Skrivebord\Grunnfiler\Vassdragsområder_Autokast.shp"
TauDEM = r"//nve.no/fil/home/htla/Dokumenter/GPHY492/INSTALL FILES/pyfiles537/TauDEM Tools.tbx"
PRATBX = r"//nve.no/fil/home/htla/Dokumenter/ArcGIS/Tool_ArcGIS-2/PRA.tbx"
HAV = r"K:\_Gis\HG\ivar\Håvard\feltpar10land.tif"

# --- Extract DEM from attribute in "Outline": (innsyn.VANN.Nedborfelt_VassOmrF -> Attribute: FID "#")
FID = arcpy.GetParameterAsText(0)

# --- Where the PRA will save intermediate results:
WorkingDirectory = rasterfolder

# --- Set Output File Names
OutputRAW = r"C:\AutokastFiles\22.11.18\Output_Files.gdb\Norge_RAW_FID%s" %FID
Output = r"C:\AutokastFiles\22.11.18\Output_Files.gdb\Norge_FID%s" %FID
Startzone_RAW = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Startzone_RAW_FID%s.tif" %FID
Startzone = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Startzone_FID%s.tif" %FID
Runout18 = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Runout18_FID%s.tif" %FID
Runout23 = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Runout23_FID%s.tif" %FID
Runout27 = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Runout27_FID%s.tif" %FID
Runout32 = r"C:\AutokastFiles\22.11.18\Output_Raster_Files\Runout32_FID%s.tif" %FID

arcpy.env.snapRaster = DEM

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# --- Edit Thresholds
# ------------------------------------------------------------------------------------------------------------------------------------------------------

# --- Class 1 Alpha Angle (Default = 18)
C1AA = 18
# --- Class 2 Alpha Angle (Default = 23)
C2AA = 23
# --- Alpha Angle (Default = 27)
C3AA = 27
# --- Alpha Angle (Default = 32)
C4AA = 32
# --- Class 0 / 1 Slope Angle Threshold (Default 15)
SAT01 = 15
# --- Class 1 / 2 Slope Angle Threshold (Default 25)
SAT12 = 25
# --- Class 2 / 3 Slope Angle Threshold (Default 40)
SAT23 = 40
# ------------------------------------------------------------------------------------------------------------------------------------------------------

def ErrorHandling(LogFile):
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    PyMsg = "PYTHON ERROR:\n" + tbinfo + "\n" + str(sys.exc_type) + ":" + str(sys.exc_value) + "\n"
    GpMsg = "GP ERROR:\n" + arcpy.GetMessages(2) + "\n"
    print PyMsg
    print GpMsg
    arcpy.AddError(PyMsg)
    arcpy.AddError(GpMsg)
    Log(LogFile, PyMsg)
    Log(LogFile, GpMsg)
    arcpy.AddMessage(arcpy.GetMessages(1))
    print arcpy.GetMessages(1)
    Log(LogFile, arcpy.GetMessages())


# ------------------------------------------------------------------------------------------------------------------------------------------------------


def Log(LogFile, logtekst):
    try:
        # ---Open the logfile
        if not arcpy.Exists(LogFile):
            OpenLogFile = open(LogFile, 'w')
        else:
            OpenLogFile = open(LogFile, 'a')

        # ---Write tekst to the logfile
        Time = time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime())
        OpenLogFile.write(Time + "   ")
        OpenLogFile.write(logtekst)
        OpenLogFile.write("\n")

        # ---Close the logfile
        OpenLogFile.close()
    except:
        # If an error occured print the message to the screen
        print "an error has occurred in function " + "Log"
        sys.exit(1)


# ------------------------------------------------------------------------------------------------------------------------------------------------------

try:
    print(glob.glob(os.path.join(rasterfolder, '*.*')))
    files = glob.glob(os.path.join(rasterfolder, '*.*'))
    for f in files:
        os.remove(f)

    print ("Old files in Raster_Folder deleted")

    # --- Make Feature Layer
    arcpy.MakeFeatureLayer_management(in_features=Outline, out_layer="vassOmr_Layer", where_clause='"FID" = %s' %FID, workspace="", field_info="FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;OBJTYPE OBJTYPE VISIBLE NONE;VASSOMR VASSOMR VISIBLE NONE")
    arcpy.CopyFeatures_management("vassOmr_Layer", os.path.join(rasterfolder, "Outline.shp"));

    print("Outline created")

    # --- Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # --- Extract's the desired DEM from the outline mask
    arcpy.gp.ExtractByMask_sa(DEM, os.path.join(rasterfolder, "Outline.shp"), os.path.join(rasterfolder, "Raster_Outline.tif"))

    # logtekst = logtekst + "\n" + "Outline created"
    print ("Raster created")

    # --- Extract's the desired DEM from the outline mask
    arcpy.gp.ExtractByMask_sa(os.path.join(rasterfolder, "Raster_Outline.tif"), HAV, os.path.join(rasterfolder, "Raster_Outline_Minus_Hav.tif"))

    # --- Raster to ASCII
    arcpy.RasterToASCII_conversion(in_raster=os.path.join(rasterfolder, "Raster_Outline_Minus_Hav.tif"), out_ascii_file=os.path.join(rasterfolder, "inputpra.asc"))

    print ("Raster to ASCII; Completed")

    # --- Load required toolboxes
    arcpy.ImportToolbox(PRATBX)

    print ("Calculating PRA")

    # --- Potential Release Area
    arcpy.gp.toolbox = PRATBX;
    arcpy.gp.PRA(os.path.join(rasterfolder, "inputpra.asc"), os.path.join(rasterfolder, "outputpra.asc"), "2,3", "Regular", "0", "180", WorkingDirectory, "")

    print ("PRA; Completed")

    # --- Define Projection For PRA
    arcpy.DefineProjection_management(in_dataset=os.path.join(rasterfolder, "outputpra.asc"), coor_system="PROJCS['WGS_1984_UTM_Zone_33N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',15.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]")

    print ("Projection Defined")

    # --- Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # --- Reclassify
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "outputpra.asc"), "VALUE", "0 0,050000 0;0,050000 1 1", os.path.join(rasterfolder, "PRA_StartZone.tif"), "DATA")

    print ("PRA Reclassified")

    # ------------------------------------------------------------------------------------------------------------------------------------------------------


    # --- Slope
    # --- Set local variables
    inRaster = os.path.join(rasterfolder, "Raster_Outline.tif")
    outMeasurement = "DEGREE"
    zFactor = 1
    # --- Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    # --- Execute Slope
    outSlope = Slope(inRaster, outMeasurement, zFactor)
    # --- Save the output
    outSlope.save(os.path.join(rasterfolder, "Slope.tif"))


    # --- Reclassify Slope
    # --- Set local variables
    inRaster = os.path.join(rasterfolder, "Slope.tif")
    reclassField = "VALUE"
    remap = RemapRange([[0, SAT01, 0], [SAT01, SAT12, 1],[SAT12, SAT23, 2],[SAT23, 90, 3]])
    # --- Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    outReclassify = Reclassify(inRaster, reclassField, remap)
    # --- Save the output
    outReclassify.save(os.path.join(rasterfolder, "Slope_Reclassify.tif"))

    print ( "Slope Calculations Completed")

    # --- CLASS 1
    # --- Local variables:
    Slope_Reclassify = os.path.join(rasterfolder, "Slope_Reclassify.tif")
    Class1 = os.path.join(rasterfolder, "Class1.tif")
    # --- Reclassify
    arcpy.gp.Reclassify_sa(Slope_Reclassify, "Value", "0 NODATA;1 1;2 NODATA;3 NODATA", Class1, "DATA")

    # --- CLASS 2
    # --- Local variables:
    Slope_Reclassify = os.path.join(rasterfolder, "Slope_Reclassify.tif")
    Class2 = os.path.join(rasterfolder, "Class2.tif")
    # --- Reclassify
    arcpy.gp.Reclassify_sa(Slope_Reclassify, "Value", "0 NODATA;1 NODATA;2 2;3 NODATA", Class2, "DATA")

    # --- CLASS 3
    # --- Local variables:
    Slope_Reclassify = os.path.join(rasterfolder, "Slope_Reclassify.tif")
    Class3 = os.path.join(rasterfolder, "Class3.tif")
    # --- Reclassify
    arcpy.gp.Reclassify_sa(Slope_Reclassify, "Value", "0 NODATA;1 NODATA;2 NODATA;3 3", Class3, "DATA")

    print ( "Slope Reclassification Calculations Completed")


    # --- RASTER TO POLYGON

    # --- CLASS 1
    # --- Set local variables
    for klasse in [1,2,3]:
        inRaster = os.path.join(rasterfolder, "Class%s.tif" %klasse)
        outPolygons = os.path.join(arcpy.env.workspace, "Class%s" %klasse)
        print outPolygons
        field = "VALUE"
        # --- Raster To Polygon
        arcpy.RasterToPolygon_conversion(inRaster, outPolygons, "NO_SIMPLIFY", field)

    print ( "Slope Calculations Converted To Shapefiles")
    # ------------------------------------------------------------------------------------------------------------------------------------------------------

    # --- Start Zones (Class 3)

    # --- Reclassify (1 = Start Zone, 0 = NoData)
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "PRA_StartZone.tif"), "Value", "0 NODATA;1 1", Startzone, "DATA")

    print ("Startzone reclassified")

    # --- Raster To Polygon
    arcpy.RasterToPolygon_conversion(in_raster=Startzone, out_polygon_features="StartZonesClass3", simplify="NO_SIMPLIFY", raster_field="Value")

    print ( "Start Zones Converted To Shapefile")
    # ------------------------------------------------------------------------------------------------------------------------------------------------------


    # --- TauDEM (Avalanche Paths; Class 1 and Class 2)

    # --- Load required toolboxes
    arcpy.ImportToolbox(TauDEM)

    # --- Pit Remove
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.PitRemove(os.path.join(rasterfolder, "Raster_Outline.tif"), "", "", "8", os.path.join(rasterfolder, "PitRemove.tif"))

    # --- D-Infinity Flow Directions
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.DinfFlowDir(os.path.join(rasterfolder, "PitRemove.tif"), "8", os.path.join(rasterfolder, "DinfFlowDirang.tif"), os.path.join(rasterfolder, "DinfFlowDirslp.tif"))

    # --- D-Infinity Avalanche Runout (Alpha Angle = 18 Degrees)
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.DInfAvalancheRunout(os.path.join(rasterfolder, "PitRemove.tif"), os.path.join(rasterfolder, "DinfFlowDirang.tif"), os.path.join(rasterfolder, "PRA_StartZone.tif"), "0,2", C1AA, "Flow Path", "8", os.path.join(rasterfolder, "DInfAvalancheRunoutrz18.tif"), os.path.join(rasterfolder, "DInfAvalancheRunoutdfs18.tif"))

    print ( "TauDEM; Alpha Angle = 18 degrees Completed")

    # --- D-Infinity Avalanche Runout (Alpha Angle = 23 Degrees)
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.DInfAvalancheRunout(os.path.join(rasterfolder, "PitRemove.tif"), os.path.join(rasterfolder, "DinfFlowDirang.tif"), os.path.join(rasterfolder, "PRA_StartZone.tif"), "0,2", C2AA, "Flow Path", "8", os.path.join(rasterfolder, "DInfAvalancheRunoutrz23.tif"), os.path.join(rasterfolder, "DInfAvalancheRunoutdfs23.tif"))

    print ( "TauDEM; Alpha Angle = 23 degrees Completed")

    # --- D-Infinity Avalanche Runout (Alpha Angle = 27 Degrees)
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.DInfAvalancheRunout(os.path.join(rasterfolder, "PitRemove.tif"), os.path.join(rasterfolder, "DinfFlowDirang.tif"), os.path.join(rasterfolder, "PRA_StartZone.tif"), "0,2", C3AA, "Flow Path", "8", os.path.join(rasterfolder, "DInfAvalancheRunoutrz27.tif"), os.path.join(rasterfolder, "DInfAvalancheRunoutdfs27.tif"))

    print ( "TauDEM; Alpha Angle = 27 degrees Completed")

    # --- D-Infinity Avalanche Runout (Alpha Angle = 32 Degrees)
    arcpy.gp.toolbox = TauDEM;
    arcpy.gp.DInfAvalancheRunout(os.path.join(rasterfolder, "PitRemove.tif"), os.path.join(rasterfolder, "DinfFlowDirang.tif"), os.path.join(rasterfolder, "PRA_StartZone.tif"), "0,2", C4AA, "Flow Path", "8", os.path.join(rasterfolder, "DInfAvalancheRunoutrz32.tif"), os.path.join(rasterfolder, "DInfAvalancheRunoutdfs32.tif"))

    print ( "TauDEM; Alpha Angle = 32 degrees Completed")

    # --- Reclassify (Alpha Angle = 18 Degrees)
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "DInfAvalancheRunoutrz18.tif"), "VALUE", "18 90 1", os.path.join(rasterfolder, "TauDEM_Reclassify18.tif"), "DATA")

    # --- Reclassify (Alpha Angle = 23 Degrees)
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "DInfAvalancheRunoutrz23.tif"), "VALUE", "18 90 1", os.path.join(rasterfolder, "TauDEM_Reclassify23.tif"), "DATA")

    # --- Reclassify (Alpha Angle = 27 Degrees)
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "DInfAvalancheRunoutrz27.tif"), "VALUE", "18 90 1", os.path.join(rasterfolder, "TauDEM_Reclassify27.tif"), "DATA")

    # --- Reclassify (Alpha Angle = 32 Degrees)
    arcpy.gp.Reclassify_sa(os.path.join(rasterfolder, "DInfAvalancheRunoutrz32.tif"), "VALUE", "18 90 1", os.path.join(rasterfolder, "TauDEM_Reclassify32.tif"), "DATA")

    # --- Boundary Clean (Alpha Angle = 18 Degrees)
    arcpy.gp.BoundaryClean_sa(os.path.join(rasterfolder, "TauDEM_Reclassify18.tif"), Runout18, "NO_SORT", "TWO_WAY")

    # --- Boundary Clean (Alpha Angle = 23 Degrees)
    arcpy.gp.BoundaryClean_sa(os.path.join(rasterfolder, "TauDEM_Reclassify23.tif"), Runout23, "NO_SORT", "TWO_WAY")

    # --- Boundary Clean (Alpha Angle = 27 Degrees)
    arcpy.gp.BoundaryClean_sa(os.path.join(rasterfolder, "TauDEM_Reclassify27.tif"), Runout27, "NO_SORT", "TWO_WAY")

    # --- Boundary Clean (Alpha Angle = 32 Degrees)
    arcpy.gp.BoundaryClean_sa(os.path.join(rasterfolder, "TauDEM_Reclassify32.tif"), Runout32, "NO_SORT", "TWO_WAY")

    # --- Raster To Polygon (Alpha Angle = 18 Degrees)
    arcpy.RasterToPolygon_conversion(in_raster=Runout18, out_polygon_features="AvalanchePathClass1", simplify="NO_SIMPLIFY", raster_field="Value")

    print ( "TauDEM; Alpha Angle = 18 degrees; Converted To Shapefile")

    # --- Raster To Polygon (Alpha Angle = 23 Degrees)
    arcpy.RasterToPolygon_conversion(in_raster=Runout23, out_polygon_features="AvalanchePathClass2", simplify="NO_SIMPLIFY", raster_field="Value")

    print ( "TauDEM; Alpha Angle = 23 degrees; Converted To Shapefile")

    # ------------------------------------------------------------------------------------------------------------------------------------------------------


    # --- Merging Data

    # --- Merge - Class 1
    arcpy.Merge_management(inputs="AvalanchePathClass1;Class1", output="Class1_Merge", field_mappings='Id "Id" true true false 10 Long 0 10 ,First,#,AvalanchePathClass1,Id,-1,-1,Class1,Id,-1,-1;gridcode "gridcode" true true false 10 Long 0 10 ,First,#,AvalanchePathClass1,gridcode,-1,-1,Class1,gridcode,-1,-1')

    # --- Dissolve - Class 1
    arcpy.Dissolve_management(in_features="Class1_Merge", out_feature_class="Class1_Dissolve", dissolve_field="gridcode", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    # --- Eliminate Polygon Part (All Clusters Smaller Than 10.000 Square Meters Are Eliminated Within The Polygon)
    arcpy.EliminatePolygonPart_management(in_features="Class1_Dissolve", out_feature_class="Class1_Eliminate", condition="AREA", part_area="10000 SquareMeters", part_area_percent="0", part_option="CONTAINED_ONLY")

    print ( "Class 1 Merged")

    # --- Merge - Class 2
    arcpy.Merge_management(inputs="AvalanchePathClass2;Class2", output="Class2_Merge", field_mappings='Id "Id" true true false 10 Long 0 10 ,First,#,AvalanchePathClass2,Id,-1,-1,Class2,Id,-1,-1;gridcode "gridcode" true true false 10 Long 0 10 ,First,#,AvalanchePathClass2,gridcode,-1,-1,Class2,gridcode,-1,-1')

    # --- Dissolve - Class 2
    arcpy.Dissolve_management(in_features="Class2_Merge", out_feature_class="Class2_Dissolve", dissolve_field="gridcode", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    # --- Eliminate Polygon Part (All Clusters Smaller Than 10.000 Square Meters Are Eliminated Within The Polygon)
    arcpy.EliminatePolygonPart_management(in_features="Class2_Dissolve", out_feature_class="Class2_Eliminate", condition="AREA", part_area="10000 SquareMeters", part_area_percent="0", part_option="CONTAINED_ONLY")

    print ( "Class 2 Merged")

    # --- Merge - Class 3
    arcpy.Merge_management(inputs="StartZonesClass3;Class3", output="Class3_Merge", field_mappings='Id "Id" true true false 10 Long 0 10 ,First,#,StartZonesClass3,Id,-1,-1,Class3,Id,-1,-1;gridcode "gridcode" true true false 10 Long 0 10 ,First,#,StartZonesClass3,gridcode,-1,-1,Class3,gridcode,-1,-1')

    # --- Dissolve - Class 3
    arcpy.Dissolve_management(in_features="Class3_Merge", out_feature_class="Class3_Dissolve", dissolve_field="gridcode", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    # --- Eliminate Polygon Part (All Clusters Smaller Than 10.000 Square Meters Are Eliminated Within The Polygon)
    arcpy.EliminatePolygonPart_management(in_features="Class3_Dissolve", out_feature_class="Class3_Eliminate", condition="AREA", part_area="10000 SquareMeters", part_area_percent="0", part_option="CONTAINED_ONLY")

    print ( "Class 3 Merged")
    # ------------------------------------------------------------------------------------------------------------------------------------------------------


    # --- Erase Data

    # --- Erase Class 2 From Class 1
    arcpy.Erase_analysis(in_features="Class1_Eliminate", erase_features="Class2_Eliminate", out_feature_class="Class1_Erase_Class2", cluster_tolerance="")
    # --- Erase Class 3 From New Class 1
    arcpy.Erase_analysis(in_features="Class1_Erase_Class2", erase_features="Class3_Eliminate", out_feature_class="Class1_Erase_Class3", cluster_tolerance="")

    print ( "Class 2 and 3 Is Overwritten Class 1")

    # --- Erase Class 3 From Class 2
    arcpy.Erase_analysis(in_features="Class2_Eliminate", erase_features="Class3_Eliminate", out_feature_class="Class2_Erase_Class3", cluster_tolerance="")

    print ( "Class 3 Is Overwritten Class 2")

    # --- Give Class 1 Value 1
    features = arcpy.UpdateCursor("Class1_Erase_Class3")
    for feature in features:
        if feature.ORIG_FID == 1:
            feature.ORIG_FID = 1
            features.updateRow(feature)
    del feature,features

    # --- Give Class 2 Value 2
    features = arcpy.UpdateCursor("Class2_Erase_Class3")
    for feature in features:
        if feature.ORIG_FID == 1:
            feature.ORIG_FID = 2
            features.updateRow(feature)
    del feature,features

    # --- Give Class 3 Value 3
    features = arcpy.UpdateCursor("Class3_Eliminate")
    for feature in features:
        if feature.ORIG_FID == 1:
            feature.ORIG_FID = 3
            features.updateRow(feature)
    del feature,features

    # --- Give Class 3 Value 3
    features = arcpy.UpdateCursor("Class3_Eliminate")
    for feature in features:
        if feature.ORIG_FID == 2:
            feature.ORIG_FID = 3
            features.updateRow(feature)
    del feature,features

    # --- Merge
    arcpy.Merge_management(inputs="Class1_Erase_Class3;Class2_Erase_Class3;Class3_Eliminate", output="KAST_Merge", field_mappings='ORIG_FID "ORIG_FID" true true false 10 Long 0 10 ,First,#,Class1_Erase_Class3,ORIG_FID,-1,-1;Class "Class" true true false 10 Long 0 10 ,First,#,Class1_Erase_Class3,ORIG_FID,-1,-1,Class2_Erase_Class3,ORIG_FID,-1,-1,Class3_Eliminate,ORIG_FID,-1,-1;Id "Id" true true false 10 Long 0 10 ,First,#,Class2_Erase_Class3,Id,-1,-1,Class3_Eliminate,Id,-1,-1')

    print ("Classes Is Merged To One Shapefile")

    # --- Dissolves Unnecessary Fields In Attribute Table
    arcpy.Dissolve_management(in_features="KAST_Merge", out_feature_class=OutputRAW, dissolve_field="Class", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    print ("Dissolve Completed")

    # --- Eliminate Polygon Part (removes clusters smaller than 1000 kvm)
    arcpy.EliminatePolygonPart_management(in_features=OutputRAW, out_feature_class="KASTEPP", condition="AREA", part_area="1000 SquareMeters", part_area_percent="0", part_option="ANY")

    print ("Eliminate Polygons < 1000 kvm Completed")

    # --- Simplify to make it more efficient for being loaded onto a web server
    arcpy.SimplifyPolygon_cartography(in_features="KASTEPP",
                                      out_feature_class=Output,
                                      algorithm="POINT_REMOVE", tolerance="10 Meters", minimum_area="0 SquareMeters",
                                      error_option="RESOLVE_ERRORS", collapsed_point_option="NO_KEEP", in_barriers="")

    print ("Simplified")

    print ("AutoKAST COMPLETED")

except:
    ErrorHandling(LogFile)
    sys.exit(1)
