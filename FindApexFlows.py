import os
import xml.etree.ElementTree as ET
import pandas as pd

def find_flows_with_apex():
    input_folder = r"C:\Muneesh\SFDXSetup\MBMeta\force-app\main\default\flows"
    output_folder = r"C:\Muneesh\SFDXSetup"


    flows_with_apex = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):
            file_path = os.path.join(input_folder, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()
            namespace = "{http://soap.sforce.com/2006/04/metadata}"

            apex_actions = root.findall(f".//{namespace}apexActions")
            if apex_actions:
                for action in apex_actions:
                    apex_class = action.find(f"{namespace}apexClass")
                    if apex_class is not None:
                        flow_name = root.find(f"{namespace}fullName").text
                        flows_with_apex.append({"Flow Name": flow_name, "File Name": filename, "Apex Class": apex_class.text})

    df = pd.DataFrame(flows_with_apex)
    output_file_path = os.path.join(output_folder, "flows_with_apex.xlsx")
    df.to_excel(output_file_path, index=False)

    print(f"Result saved to {output_file_path}")

find_flows_with_apex()
