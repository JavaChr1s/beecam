import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import sys
import os.path

def xml_to_csv(path, set_type = "TRAINING"):
    xml_list = []
    for xml_file in glob.glob(path + '/**/*.xml', recursive=True):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        image_path_from_xml = os.path.basename(root.find('path').text)
        image_filename_from_xml = image_path_from_xml.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        recursive_path = xml_file.rsplit('/', 1)[0].rsplit(path, 1)[1]
        image_path = recursive_path + '/' + image_filename_from_xml
        if ( image_path_from_xml.endswith(".jpg")):
            if os.path.isfile(path + '/' + image_path):
                size = root.find("size")
                width = int(size.find("width").text)
                height = int(size.find("height").text)
                for member in root.findall('object'):
                    value = (set_type,
                         image_path,
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
            else:
            	print(f"Image for XML not found {xml_file}")
    column_name = ['set','filename', 'class', 'xmin', 'ymin', 'xmax', 'ymax', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main(argv):
    image_path = os.path.join(os.getcwd())
    xml_df = xml_to_csv(argv[1], argv[2])
    xml_df.to_csv('temp/' + argv[2] + '_labels.csv', index=None, header=False)
    print('Successfully converted xml to csv.')


main(sys.argv)

