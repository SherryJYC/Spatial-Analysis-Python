import os
import numpy as np


class Facility:
    '''

Facility is a class used to handle one certain facility type.
Parameters:
workspace: workspace for arcpy
list: Infor of facilities, each row has format [factype, name, address, lon, lat, easting, northing, admdis]
type: facilitity type

    '''

    def __init__(self):
        self.workspace = ''
        self.list = []
        self.type = ""

    def Read_From_File(self, filename):
        temp = []
        try:
            f = open(filename)
            for index, line in enumerate(f):
                elements = line.replace("\n", " ").split("\t")
                factype = elements[0]
                name = elements[1]
                address = elements[2]
                lon = float(elements[3])
                lat = float(elements[4])
                easting = float(elements[5])
                northing = float(elements[6])
                if len(elements) > 7:
                    admdis = elements[7]
                else:
                    admdis = 'NoData'
                temp = [factype, name, address, lon, lat, easting, northing, admdis]
                self.list.append(temp)

            self.type = self.list[0][0].replace('"', '')
            print "Complete Reading This File: ", filename
            f.close()
        except IOError:
            print "Failure to open file."

    def Find_Diver(self):  # find the number of facilities in each district
        adminArray = np.array(np.asarray(self.list)[:, 7])
        unique_elements, counts_elements = np.unique(adminArray, True)
        np.savetxt(self.type + ".csv", np.asarray([unique_elements, counts_elements]), delimiter=",",
                   fmt="%s")  # save output as csv file
        self.adminCnt = len(unique_elements)
        # print self.adminCnt
        print "Exploration of Diversity Done"
        print "Admin Name and Counts"
        print counts_elements  # number of facilities in certain district
        print unique_elements  # name of district
        return counts_elements, unique_elements


class FacStore:
    '''

Facility store can handle different facility types and there is no need to specify every filename and create different facility onr by one.
Parameters:
workspace: workspace for arcpy
fac_list: list of facility objects
dist: list used when finding nearest facility [this_fac.type, min_dist]

    '''

    def __init__(self):
        self.workspace = ''  # path to working database
        self.fac_list = []  # list of facility objects
        self.dist = []  # [this_fac.type, min_dist]

    def Read_From_Dir(self, file_dir):  # find all files in file_dir and handle different facility objects
        for file in os.listdir(file_dir):
            if file.endswith(".txt"):
                filename = os.path.join(file_dir, file)
                this_fac = Facility()
                this_fac.Read_From_File(filename)
                self.fac_list.append(this_fac)

        print "Complete Reading ALL Files"

    def Find_Global_Diver(self,
                          find_area):  # find [number of facility types, total number of facilities] in each district
        for this_fac in self.fac_list:
            counts_elements, unique_elements = this_fac.Find_Diver()
            for key, item in find_area.iteritems():
                for index, name in enumerate(unique_elements):
                    if key == name and counts_elements[index] > 0:
                        item[0] += 1
                        item[1] += counts_elements[index]
        print "Exploration of ALL files's Diversity Done: District Name: [types, counts]"
        print find_area
        return find_area


if __name__ == "__main__":
    workpath = r"D:\15104163D\project"  # workpath to folder containing geodatabase r"D:\15104163D\project\"
    dbname = 'facility.gdb'  # name of geodatabase facility.gdb
    workspace = os.path.join(workpath, dbname)  # absolute path to geodatabase
    file_dir = r"D:\15104163D\project\txt_file"  # directory containing all txt files

    # trial for handling one certain facility===============================================
    filename="sports_grounds.txt"
    fac=Facility()
    fac.Read_From_File(os.path.join(file_dir, filename))
    counts, unique_admin=fac.Find_Diver()


    # trial for handling ALL facilities========================================================
    store = FacStore()
    store.Read_From_Dir(file_dir)

    # find facility type distribution in certain area
    find_area = {'EASTERN ': [0, 0], 'ISLANDS ': [0, 0],
                 'KOWLOON CITY ': [0, 0], 'KWAI TSING ': [0, 0],
                 'KWUN TONG ': [0, 0], 'NORTH ': [0, 0],
                 'SAI KUNG ': [0, 0], 'SHA TIN ': [0, 0],
                 'SHAM SHUI PO ': [0, 0], 'SOUTHERN ': [0, 0],
                 'TAI PO ': [0, 0], 'TSUEN WAN ': [0, 0],
                 'TUEN MUN ': [0, 0], 'WAN CHAI ': [0, 0],
                 'WONG TAI SIN ': [0, 0], 'YUEN LONG ': [0, 0],
                 'YAU TSIM MONG ': [0, 0], 'CENTRAL & WESTERN ': [0, 0]
                 }
    find_area = store.Find_Global_Diver(find_area)

    print "All Tasks Successfully Done"
