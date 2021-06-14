# test_str = '3.4.2-A Coruña'
# compare = int(test_str.split('-')[0].split('.')[1])
# print(compare)
# print('true') if compare >= 2 else print('false')

import os
from shutil import copyfile

src = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\poi_visibility_network\work_folder\POI\results_file\final.shp'
res_folder = r'C:\Users\achituv\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\poi_visibility_network\results'

src = src[:-4]
dst = os.path.join(res_folder, 'sight_node')
for ext in ['.shp', '.dbf', '.prj', '.shx']:
    copyfile(src + ext, dst + ext)
