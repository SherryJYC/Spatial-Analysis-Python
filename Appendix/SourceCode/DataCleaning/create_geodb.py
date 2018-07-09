import arcpy
if __name__=='__main__':
    workspace = r"D:\15102733d\project_workspace2"
    geoDB = "project.gdb"
    arcpy.env.workspace=workspace
    arcpy.CreateFileGDB_management(workspace,geoDB)
    print ("Complete creating GeoDB")