import arcpy
arcpy.env.overwriteOutput =True
import arcpy.stats


class LicenseError(Exception):
    pass
try:
    if arcpy.CheckExtension("Spatial")=="Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        raise LicenseError
    arcpy.env.workspace= r"D:\15102733d\project_workspace2\project.gdb"
except LicenseError:
    print("Spatial Analysis license is unavailable!")
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))


def Base_Map_Clean(basemap_list):
    '''
    To copy the basemap shapefile as feature class and delete unneccessary fields
    :param basemap_list: basemap shapefile and feature class name list
    :return:
    '''
    in_shapefile=basemap_list["shapefile_path"]
    arcpy.CopyFeatures_management(in_shapefile,basemap_list['basemap'])
    arcpy.CopyFeatures_management(basemap_list["basemap"],basemap_list["basemap_cleaned"])
    arcpy.DeleteField_management(basemap_list["basemap_cleaned"],["NAME_1","ID_0","ISO","NAME_0","ID_1","VARNAME_1","NL_NAME_1",
                                                               "HASC_1","CC_1","TYPE_1","ENGTYPE_1","VALIDFR_1","VALIDTO_1",
                                                               "REMARKS_1","Shape_Leng","Shape_Le_1"])
    print("Clean data from basemap completed!")


def Test_Locked(basemap_list,facility_list):
    '''
    To test if there is feature class locked
    :param basemap_list: feature class name
    :param facility_list: feature class name
    :return:
    '''
    for key,value in basemap_list.items():
        if not arcpy.TestSchemaLock(value):
            print("Feature class "+value+" is locked!")
        else: print("Feature class "+value+" is not locked!" )
    for key,value in facility_list.items():
        if not arcpy.TestSchemaLock(value):
            print("Feature class "+value+" is locked!")
        else: print("Feature class "+value+" is not locked!" )

def Dissolve_BaseMap():
    '''
    To dissolve the polygons in basemap
    :return:
    '''
    try:
        arcpy.Dissolve_management("basemap_cleaned","basemap_dissolved")
        print "Complete dissolving basemap"
    except:
        print(arcpy.GetMessages())


def Optimized_HotSpot_Analysis(facilityName):
    '''
    To conduct Optimized Hot Spot Analysis
    :param facilityName: feature class name of the facility
    :return:
    '''
    try:
        #Get the raster dataset of facility density surface
        arcpy.env.mask = "basemap_dissolved"
        arcpy.MinimumBoundingGeometry_management(facilityName,facilityName+"_MBG","CONVEX_HULL","ALL","#","NO_MBG_FIELDS")
        ohsa = arcpy.OptimizedHotSpotAnalysis_stats(facilityName,facilityName+"_ohsaSnap","","SNAP_NEARBY_INCIDENTS_TO_CREATE_WEIGHTED_POINTS",
                                                   facilityName+"_MBG","",facilityName+"_ohsaRaster" )
        ohsa2 = arcpy.OptimizedHotSpotAnalysis_stats(facilityName, facilityName+"_ohsaFishnet","","COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS",
                                                     "basemap_dissolved")
        if arcpy.Exists(facilityName+"_MBG"):
            arcpy.Delete_management(facilityName+"_MBG")
        print "Complete hot spot analysis"
    except:
        print (arcpy.GetMessages())


def Convert_OHSA_BASEMAP(facilityName,workspacePath):
    '''
    To convert the range of OHSA output raster into basemap range
    :param facilityName: feature class name of facility
    :param workspacePath: geodb workspace path
    :return:
    '''
    try:
        #convert hkbasemap into raster
        arcpy.AddField_management("basemap_cleaned","Value","FLOAT")#,field_is_nullable="NON_NULLABLE")
        cursor = arcpy.UpdateCursor("basemap_cleaned")
        for row in cursor:
            row.setValue("Value",0)
            cursor.updateRow(row)
        arcpy.PolygonToRaster_conversion("basemap_cleaned","Value","basemap_raster")
        #Union hkbasemap_raster and ohsa
        arcpy.CopyRaster_management("basemap_raster","basemap_raster_32bit",pixel_type="32_BIT_FLOAT")
        print "############################################################"
        arcpy.MosaicToNewRaster_management(["basemap_raster_32bit",facilityName+"_ohsaRaster"],workspacePath,
                                           facilityName+"_densitySurface",number_of_bands=1,pixel_type="32_BIT_FLOAT")
        print "Complete convert range of ohsaraster to basemap"
    except:
        print (arcpy.GetMessages())


def Check_OHSA_Result(facilityList):
    '''
    To find out feature classes which cannot be analyzed by ohsa
    :param facilityList: feature class name list of facilities
    :return: a list including feature class names of those cannot be analyzed by ohsa
    '''
    try:
        unanalysis_facility_list =[]
        for key,value in facilityList.items():
            if not arcpy.Exists(value+"_ohsaRaster"):
                unanalysis_facility_list.append(value)
            if arcpy.Exists(value + "_MBG"):
                arcpy.Delete_management(value + "_MBG")
        print "Complete checking unanalysis facilities"
        return unanalysis_facility_list
    except:
        print(arcpy.GetMessages())


def Merge_Facilities(facilityList,output):
    '''
    To merge the feature classes with the same feature type
    :param facilityList: list of feature class names to be merged
    :param output: output feature class name
    :return: output feature class name
    '''
    try:
        arcpy.Merge_management(facilityList, output)
        print "Complete merging facilities"
        return output
    except:
        print(arcpy.GetMessages())


def Nearest_Neighbour_Index_Analysis(facilityName):
    '''
    To conduct Nearest Neighbour Index Analysis
    :param facilityName: feature class name to be analyzed
    :return:
    '''
    try:
        nn_output = arcpy.AverageNearestNeighbor_stats(facilityName, "EUCLIDEAN_DISTANCE", "GENERATE_REPORT", "#")

        # Create list of Average Nearest Neighbor output values by splitting the result object
        # print("The nearest neighbor index is: " + nn_output[0])
        # print("The z-score of the nearest neighbor index is: " + nn_output[1])
        # print("The p-value of the nearest neighbor index is: " + nn_output[2])
        # print("The expected mean distance is: " + nn_output[3])
        # print("The observed mean distance is: " + nn_output[4])
        # print("The path of the HTML report: " + nn_output[5])
        print "Complete Nearest Neighbour Analysis"
    except:
        print(arcpy.GetMessages())


if __name__=='__main__':
    basemap_info={
        "basemap_cleaned":"basemap_cleaned",
        "basemap":"basemap",
        "shapefile_path":r"E:\System_Customization\Final_project\Data for Final Project\HK Map\basemap_hk1980_population.shp"
    }
    facility_list={
        "basketball":"basketball_court",
        "fitness":"fitness_center",
        "other":"other_recreation_sports_facilities",
        "parks":"parks_gardens",
        "grounds":"sports_grounds",
        "swimming":"swimming_pools",
        "badminton":"badminton_court",
        "country":"country_parks"
        # "nearest":"pointFeature",
        # "nearest_facility":"Nearest_Facility"
    }
    ## Test if the feature class is locked or not
    # Test_Locked(basemap_list,facility_list)

    ## Clean unneccesary fields in basemap
    Base_Map_Clean(basemap_info)


    ######### Spatial Distribution Analysis #########
    ### Type in the workspace path here, then run the code
    workspace_path=r"D:\15102733d\project_workspace2\project.gdb"

    # Dissolve base map
    Dissolve_BaseMap()

    ##### Simple facility analysis #####
    for key,value in facility_list.items():
        # Spatial Pattern Analysis
        # Html file path: C:\Users\TEMPLS~1.001\AppData\Local\Temp\NearestNeighbor_Result.html
        Nearest_Neighbour_Index_Analysis(value)
        # Optimized Hot Spot Analysis for getting spatial distribution
        Optimized_HotSpot_Analysis(value)
        Convert_OHSA_BASEMAP(value,workspace_path)

    ##### Facilities which cannot be analyzed by Hot Spot #####
    unanalysised_facilities = Check_OHSA_Result(facility_list)
    unanalysised_facility_merge = Merge_Facilities(unanalysised_facilities,"Unanalysis_Facility")
    Optimized_HotSpot_Analysis(unanalysised_facility_merge)
    Convert_OHSA_BASEMAP(unanalysised_facility_merge,workspace_path)
    Nearest_Neighbour_Index_Analysis(unanalysised_facility_merge)

    ##### All facilities #####
    all_facility = Merge_Facilities([value for key,value in facility_list.items()],"All_Facilities")
    Optimized_HotSpot_Analysis(all_facility)
    Convert_OHSA_BASEMAP(all_facility, workspace_path)
    Nearest_Neighbour_Index_Analysis(all_facility)

