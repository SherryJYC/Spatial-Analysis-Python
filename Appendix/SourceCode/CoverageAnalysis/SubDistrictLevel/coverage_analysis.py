import arcpy
arcpy.env.overwriteOutput=True


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



def Create_Fishnet():
    '''
    Create fishnets for basemap_cleaned
    :return:
    '''
    try:

        origin_coord="800976.4051000001 801661.3544999994"
        axis_coord="800976.4051000001 801671.3544999994"
        arcpy.CreateFishnet_management("basemap_Fishnet",cell_height=250,cell_width=250,
                                       origin_coord=origin_coord,y_axis_coord=axis_coord,
                                       # labels="LABELS",
                                       template="basemap_cleaned",geometry_type="POLYGON")
        arcpy.AddField_management("basemap_Fishnet","Types","INTEGER")
        cursor=arcpy.UpdateCursor("basemap_Fishnet")
        for row in cursor:
            row.setValue("Types",0)
            cursor.updateRow(row)
        del row,cursor
        print("Complete creating basemap fishnets!")
    except:
        print(arcpy.GetMessages())


def Near_Analysis(facilityFeature, searchRadius=500):
    '''
    Conduct near analysis to select positions which have facilities within 500 meters (default) around
    :param facilityFeature: facility feature class name
    :return:
    '''
    try:
        inLayer="facility_selected"
        arcpy.Near_analysis("basemap_Fishnet",facilityFeature,searchRadius,"LOCATION")
        arcpy.MakeFeatureLayer_management("basemap_Fishnet", inLayer)
        arcpy.CopyFeatures_management(inLayer,"coverage_"+facilityFeature)
        arcpy.AddField_management("coverage_"+facilityFeature,"Types","INTEGER")
        cursor=arcpy.UpdateCursor("coverage_"+facilityFeature)
        for row in cursor:
            dist=row.getValue("NEAR_DIST")
            if dist>=0:
                row.setValue("Types",1)
            else:
                row.setValue("Types",0)
            cursor.updateRow(row)
        del row,cursor
        print("Complete Near Analysis for "+facilityFeature+"!")

    except:
        print(arcpy.GetMessages())

def Coverage_Analysis(facility_list,facility_raster_list):
    '''
    Add up all facilities in one raster layer, filter places which are surrounded 
        by at least 3 types of facilities
    :param facility_list: facility feature class name list
    :param facility_raster_list: name list for facility raster layer
    :return:
    '''
    try:
        for i in range(len(facility_list)):
            arcpy.PolygonToRaster_conversion("coverage_"+facility_list[i],"Types",facility_raster_list[i])
        cellstatistics= arcpy.sa.CellStatistics(facility_raster_list,"SUM","DATA")
        filter_coverage=arcpy.sa.Con(cellstatistics,cellstatistics,"","Value>=3")
        coverage_majority=arcpy.sa.MajorityFilter(filter_coverage,'EIGHT', majority_definition='MAJORITY')
        coverage_majority.save("Coverage_Raster")
        print "Complete coverage analysis"
    except:
        print(arcpy.GetMessages())
def Delete_Unrequired_Data(facility_raster_list,facility_list):
    '''
    Delete unnecessary feature classes and raster layers
    :param facility_raster_list: raster layer list
    :param facility_list: facility name list
    :return:
    '''
    for raster in facility_raster_list:
        if arcpy.Exists(raster):
            arcpy.Delete_management(raster)
    for facility in facility_list:
        if arcpy.Exists("coverage_"+facility):
            arcpy.Delete_management("coverage_"+facility)
    print "Complete deleting unrequired data~"
def Intersect_To_Basemap():
    '''
    Intersect the filtered good coverage places to hk basemap_cleaned
    :return:
    '''
    try:
        arcpy.RasterToPolygon_conversion("Coverage_Raster","Coverage_Polygon")
        arcpy.Intersect_analysis(["basemap_cleaned","Coverage_Polygon"],"coverage_basemap")
        if arcpy.Exists("Coverage_Polygon"):
            arcpy.Delete_management("Coverage_Polygon")
        print("Complete join to basemap")

    except:
        print(arcpy.GetMessages())


if __name__=="__main__":
    #Type in the workspace here and then run the codes
    workspace = r"D:\15102733d\project_workspace2\project.gdb"
    facility_list=[
         "basketball_court",
         "fitness_center",
         "other_recreation_sports_facilities",
         "parks_gardens",
        "sports_grounds",
         "swimming_pools",
         "badminton_court",
         "country_parks"
    ]
    facility_raster_list=[]
    for i in range(len(facility_list)):
        facility_raster_list.append(facility_list[i]+"_Raster")
    Create_Fishnet()
    for i in range(len(facility_list)):
        Near_Analysis(facility_list[i])
    Coverage_Analysis(facility_list,facility_raster_list)
    Intersect_To_Basemap()
    Delete_Unrequired_Data(facility_raster_list,facility_list)