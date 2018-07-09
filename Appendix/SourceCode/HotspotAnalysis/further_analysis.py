import arcpy
from arcpy.sa import *
arcpy.env.overwriteOutput =True
import xlwt

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


def Filter_Fishnet(featureName,txtPath):
    '''
    Filter vector fishnet to get hot or cold spot area
    :param featureName: feature class name of fishnet
    :param txtPath: path of txt file which will store the output district names
    :return:
    '''
    try:
        inFeature = featureName+"_intersect"
        inLayer = featureName+"_layer"
        output = featureName+"_FishnetFilter"

        arcpy.Intersect_analysis([featureName,"basemap_cleaned"],inFeature)
        arcpy.MakeFeatureLayer_management(inFeature,inLayer)
        arcpy.SelectLayerByAttribute_management(inLayer,"NEW_SELECTION",'"Gi_Bin">=3')
        arcpy.SelectLayerByAttribute_management(inLayer,'ADD_TO_SELECTION','"Gi_Bin"<0')
        arcpy.CopyFeatures_management(inLayer,output)
        print("Complete filtering fishnet!")

        rows = arcpy.da.SearchCursor(output,'name')
        districtList=[]
        for row in rows:
            districtList.append(row)
        districtListFinal=list(set(districtList))
        print districtListFinal
        # print len(districtListFinal)
        f=open(txtPath,'a')
        f.write("========The outcome of "+featureName+" Fishnet Filter District Name==========\n")
        for i in districtListFinal:
            f.write(i[0].encode('utf-8'))
            f.write('\n')
        f.close()
        print("Complete writing filtered district names into txt file!")
    except:
        print(arcpy.GetMessages())
def Filter_Snap(facilityName):
    '''
    Slice and filter the raster layer
    :param facilityName: name of raster
    :return:
    '''
    try:
        reclassLevel = 10
        sliceFacility = Slice(facilityName,reclassLevel)

        outConHot = Con(sliceFacility,sliceFacility,'',"Value>=8")
        outHotMajFilt = MajorityFilter(outConHot, 'EIGHT', majority_definition='MAJORITY')
        outHotMajFilt.save(facilityName+'_SnapFilter_Hotspot')

        outConCool =Con (sliceFacility,sliceFacility,'',"Value<=2")
        outCoolMajFilt = MajorityFilter(outConCool, 'EIGHT', majority_definition='MAJORITY')
        outCoolMajFilt.save(facilityName+"_SnapFilter_Coldspot")

        print("Complete filtering snap!")
    except:
        print(arcpy.GetMessages())
def Spot_Area_Selection(facilityName):
    '''
    Select hot or cold spot areas
    :param facilityName: feature class name of input
    :return:
    '''
    try:
        in_raster=["Hotspot","Coldspot"]
        Poly=[]
        Dissolved=[]
        for i in range(len(in_raster)):
            arcpy.RasterToPolygon_conversion(facilityName+in_raster[i],facilityName+in_raster[i]+"Poly","NO_SIMPLIFY")
            arcpy.Dissolve_management(facilityName+in_raster[i]+"Poly",facilityName+in_raster[i]+"Dissolved")
            arcpy.Intersect_analysis([facilityName+in_raster[i]+"Dissolved","basemap_cleaned"],facilityName+in_raster[i]+"_District")
            # Delete feature classes in processing
            Poly.append(facilityName+in_raster[i]+"Poly")
            Dissolved.append(facilityName+in_raster[i]+"Dissolved")
            if arcpy.Exists(Poly[i]): arcpy.Delete_management(Poly[i])
            if arcpy.Exists(Dissolved[i]):arcpy.Delete_management(Dissolved[i])
            print("Complete Spot Area Selection!")
    except:
        print(arcpy.GetMessages())
def Read_Attribute_Table_To_EXCEL(featureClass,hotorcold):
    '''
    To write the attribute table of feature class into excel file
    :param featureClass: feature class name of input
    :param hotorcold: select hot or cold spot analysis
    :return:
    '''
    arcpy.CalculateAreas_stats(featureClass,featureClass+"Area")
    rows = arcpy.da.SearchCursor(featureClass+"Area", ['name','F_AREA'])
    wb = xlwt.Workbook()
    ws = wb.add_sheet(hotorcold)
    ws.write(0,0,featureClass+"Area")
    ws.write(1,0,"Area")
    r = 1
    sum=0
    for row in rows:
        ws.write(0, r, row[0].encode('utf-8'))
        ws.write(1, r, row[1])
        sum+=row[1]
        r += 1
    ws.write(0,r,"SUM")
    ws.write(1,r,sum)
    wb.save(hotorcold+'.xls')
    if arcpy.Exists(featureClass+"Area"):
        arcpy.Delete_management(featureClass+"Area")
    print("Complete reading name and area to excel file!")


if __name__=='__main__':
    fishNet_list={
        "allFacility":"All_Facilities_ohsaFishnet",
        "badminton":"badminton_court_ohsaFishnet",
        "basketball":"basketball_court_ohsaFishnet",
    }
    snap_list = {
        "allFacility": "All_Facilities_densitySurface",
        "badminton": "badminton_court_densitySurface",
        "basketball": "basketball_court_densitySurface",
    }
    snap_filter_list={
        "allFacility": "All_Facilities_densitySurface_SnapFilter_",
        "badminton": "badminton_court_densitySurface_SnapFilter_",
        "basketball": "basketball_court_densitySurface_SnapFilter_",
    }
    hot_cold_district=["Hotspot_District","Coldspot_District"]
    #Filter fishnets
    # Please insert the path for output txt
    Filter_Fishnet(fishNet_list['allFacility'],txtPath=r"D:\15102733d\project_workspace2\fishnetFilterDistrict.txt")
    #Filter snap
    Filter_Snap(snap_list['allFacility'])


    # print hot and cold spot area per district
    Spot_Area_Selection(snap_filter_list['allFacility'])
    for i in range(len(hot_cold_district)):
        Read_Attribute_Table_To_EXCEL(snap_filter_list['allFacility']+hot_cold_district[i],hot_cold_district[i])
