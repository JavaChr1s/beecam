import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import sys

def xml_to_csv(path, set_type = "TRAINING"):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        size = root.find("size")
        width = int(size.find("width").text)
        height = int(size.find("height").text)
        for member in root.findall('object'):
            if ( os.path.basename(root.find('path').text).endswith(".jpg")):
                value = (set_type,
            	     os.path.basename(root.find('path').text),
                     member[0].text,
                     1 / width * int(member[4][0].text),
                     1 / height * int(member[4][1].text),
                     "",
                     "",
                     1 / width * int(member[4][2].text),
                     1 / height * int(member[4][3].text),
                     "",
                     ""
                     )
                xml_list.append(value)
    column_name = ['set','filename', 'class', 'xmin', 'ymin', 'xmax', 'ymax', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main(argv):
    image_path = os.path.join(os.getcwd())
    xml_df = xml_to_csv(argv[1], argv[2])
    xml_df.to_csv('temp/' + argv[2] + '_labels.csv', index=None, header=False)
    print('Successfully converted xml to csv.')


main(sys.argv)

