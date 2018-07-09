import csv


def dms_to_dd(coord):
    '''
    Convert DMS into DD
    :param coord: point coordinate in Degree-Minute-Second
    :return: point coordinate in Decimal Degree
    '''
    [d,m,s] = coord.split('-')

    dms = str(float(d)+float(m)/60+float(s)/3600)
    return dms


def clean_data(fileName):
    '''
    Clean the data in .csv and store the data into .txt file
    :param fileName: the name of .csv file without extension
    :return:
    '''
    pointList = []
    with open(filePath+"/"+fileName+".csv", encoding='utf-16') as csvFile:
        readerObj = csv.reader(csvFile, delimiter='\t')
        next(readerObj, None)
        for row in readerObj:
            ftype = row[0]
            name = row[2]
            address = row[4]
            lon = dms_to_dd(row[6])
            lat = dms_to_dd(row[8])
            x = row[10]
            y = row[12]
            district = row[14]
            temp = [ftype, name, address, lon, lat, x, y, district]
            pointList.append(temp)
            print(temp)
    print(pointList)
    csvFile.close()
    with open(filePath+'/cleaned_data/'+fileName+".txt", 'w') as output:
        for point in pointList:
            output.write('\t'.join(point))
            output.write('\n')
    output.close()
    print('completing creating txt file')


if __name__ == '__main__':
    # Please input the path of the directory storing csv files
    filePath = r"/Volumes/HP/System_Customization/Final_project/Data for Final Project"
    fileList = ["basketball_court",
                "fitness_center",
                "other_recreation_sports_facilities",
                "parks_gardens",
                "sports_grounds",
                "swimming_pools",
                "badminton_court",
                "country_parks"]
    for file in fileList:
        clean_data(file)