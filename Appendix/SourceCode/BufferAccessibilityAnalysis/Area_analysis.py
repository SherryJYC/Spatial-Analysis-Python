import arcpy
from arcpy import env
import xlwt


# check out the ArcGIS Spatial Analyst extension license and set the workspace

arcpy.CheckOutExtension("Spatial")
env.workspace = r'D:/15103228D/project.gdb'

def Buffer_Area(input_feature, out_feature, type_no, distance):
    # this function aims to find the area within reasonable walking distance to specified facility type

    if arcpy.Exists(out_feature[type_no]):
        arcpy.Delete_management(out_feature[type_no])
    # take correspond feature class into Buffer_Analysis function, based on type_no that user entered
    in_feature = input_feature[type_no]
    out_feature_class = out_feature[type_no]
    
    arcpy.Buffer_analysis(in_feature, out_feature_class, distance,'FULL','ROUND','ALL')
    print 'complete buffer analysis !'

    if arcpy.Exists('target_area_'+input_feature[type_no]):
        arcpy.Delete_management('target_area_'+input_feature[type_no])

    output_features = 'target_area_'+input_feature[type_no]
    input_features = [out_feature[type_no], 'basemap_cleaned']
    
    arcpy.Intersect_analysis(input_features,output_features,'ALL','','INPUT')

    print '=================================================='
    print '*****************    complete    ******************'

def Accessibility_analysis(dist):

    """
    this function combine the highway connection in HK,
    to analysis how many facilities are accessible within specified distance to main roads.
    """
    # get the intersection area of HK base map and highway connection
    if arcpy.Exists('HK_mainroad'):
        arcpy.Delete_management('HK_mainroad')
    input_files = ['HK_Highway','basemap_cleaned']
    output_files = 'HK_mainroad'
    arcpy.Intersect_analysis(input_files,output_files ,'ALL','','INPUT') # create intersected feature class

    if arcpy.Exists('highway_buffer'):
        arcpy.Delete_management('highway_buffer')
    
    # use Buffer_analysis create the buffer around the road network

    arcpy.Buffer_analysis('HK_mainroad','highway_buffer', dist,'FULL','ROUND','ALL')
    print 'Highway buffer created !'

    # Merge all the point feature classes into one feature class using merge_managementb 
    if arcpy.Exists('all_points'):
        arcpy.Delete_management('all_points')
    class_list=['Swimming_pools','Sports_ground','Recreation_facilities','Park_gardens','Fitness_center','country_parks','Basketball_court','Badminton_court']
    arcpy.Merge_management(class_list, 'all_points')
    print 'Merge finished !'

    # make all_point feature class as layer
    '''
    select all the facilities within road buffer by using SelectLayerByLocation_management,
    and store them in a new feature class named 'near_facility'
    '''

    arcpy.MakeFeatureLayer_management('all_points','all_points_layer' )
    arcpy.SelectLayerByLocation_management('all_points_layer',"INTERSECT",'highway_buffer','0', "NEW_SELECTION")
    if arcpy.Exists('near_facility'):
        arcpy.Delete_management('near_facility')
    arcpy.CopyFeatures_management('all_points_layer', 'near_facility')
    print 'complete locating near facilities !'

    cursor_out = arcpy.da.SearchCursor('near_facility', ['Type'])
    # to record the number of each facility within the road buffer
    counter1=counter2=counter3=counter4=counter5=counter6=counter7=counter8=0
    for row in cursor_out:
        if row[0] == 'Swimming Pools':
            counter1+=1
        elif row[0] == 'Sports Grounds':
            counter2+=1
        elif row[0] == 'Other Recreation & Sports Facilities':
            counter3+=1
        elif row[0] == '"Parks, Zoos and Gardens"':
            counter4+=1
        elif row[0] == 'Fitness Rooms':
            counter5+=1
        elif row[0] == 'Country Parks':
            counter6+=1
        elif row[0] == 'Basketball Courts':
            counter7+=1
        elif row[0] == 'Badminton Courts':
            counter8+=1
    # store the the name of facility type and couunt result in two lists
    label = ['Swimming Pools','Sports Grounds','Other Recreation & Sports Facilities','Parks, Zoos and Gardens',
             'Fitness Rooms','Country Parks','Basketball Courts','Badminton Courts']
    counter=[counter1,counter2,counter3,counter4,counter5,counter6,counter7,counter8]

    # count the total number of items in near_facility feature class
    result = arcpy.GetCount_management('near_facility')

    # convert the type of 'result' to string, and tehen can be transformed into int for calculation
    count_no = str(result)

    # write count result into excel file
    wb = xlwt.Workbook()
    ws = wb.add_sheet('calculation Result')
    ws.write(0, 0, 'Name')
    ws.write(1, 0, 'Number')
    ws.write(0,9,'Sum')
    ws.write(1,9,count_no)
    for i in range(1, 9):
        ws.write(0, i, label[i - 1])
        ws.write(1, i, counter[i - 1])
    wb.save('Output.xls')
    print 'Complete writing output file !'

    print '**************************   Output   ******************************'
    print 'The number of each facility in highway buffer area:'
    for i in range(0,8):
        print label[i], ': ',counter[i]
    
    # calculate the total accessibility rate
    print'**************************   Accessibility Rate   ******************************'
    print 'The accessibility Rate of facilities within ',dist,'m to Highway is: '
    print int(count_no)* 100/678,'%'

if __name__=='__main__':
    
    # The name of input feature class and output buffer feature class are stored in lists
    in_name = [
        'Badminton_court',
        'Basketball_court',
        'country_parks',
        'Fitness_center',
        'Recreation_facilities',
        'Park_gardens',
        'Sports_ground',
        'Swimming_pools'
    ]
    out_name = [
        'Badminton_Buffer',
        'Basketball_Buffer',
        'country_parks_Buffer',
        'Fitness_center_Buffer',
        'Recreation_facilities_Buffer',
        'Park_gardens_Buffer',
        'Sports_ground_Buffer',
        'Swimming_pools_Buffer'
    ]

    # get user-specified distance from keyboard and error handling
    print '============================================================='
    print '**********************   WELCOME   ***************************'
    condition = input(" Use default distance (1000 m)?(Yes--1;No--2) ")
    if condition == 1:
        input_dist = 1000  # dafault search walking distance
    elif condition == 2:
        input_dist = input(" Enter user specified distance (Meter): ")
    else:
        print 'Invalid input! Take default distance "1000 m" as input.'
        input_dist = 1000
   
    # get user specified facility type from keyboard
    print '*************** Input Facility Type Number(1-8) *******************'
    for i in range(0, 8):
        print 'Option', i + 1, ': ', in_name[i]
    Input_value = input(" **************************   Facility Type = ?  ***************************")
    if Input_value in range (1,8):
        user_input_type = Input_value
    else:
        print 'Invalid input value! Take option (1) as default facility type. '
        user_input_type = 1 # default facility type

    Buffer_Area(in_name, out_name, user_input_type-1, input_dist)

    print '******************* Accessibility Analysis ********************: '
    dist_road = input('Enter specified distance from highway (Meter): ')
    Accessibility_analysis(dist_road)