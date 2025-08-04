import os
import xml.etree.ElementTree as ET
import csv
import re

object_name = "CoMarketing__c"
input_folder = "C:\\Muneesh\\ApprovalProcesses\\unpackaged\\approvalProcesses"
ns = {"sf": "http://soap.sforce.com/2006/04/metadata"}
output_file = "C:\\Muneesh\\entry_criteria_results.csv"

def formula_to_soql(formula):
    soql = f"SELECT Id FROM {object_name}"
    conditions = formula.replace("&&", " AND ").replace("||", " OR ")
    conditions = re.sub(r'NOT\(ISNULL\((.*?)\)\)', r'\1 != null', conditions)
    conditions = re.sub(r'ISNULL\((.*?)\)', r'\1 = null', conditions)
    conditions = re.sub(r'ISBLANK\((.*?)\)', r'\1 = null', conditions)
    conditions = re.sub(r'BLANKVALUE\((.*?),(.*?)\)', r'COALESCE(\1, \2)', conditions)
    conditions = conditions.replace("TEXT(", "").replace(")", "")
    if conditions:
        soql += f" WHERE {conditions}"
    return soql

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["File Name", "Entry Criteria Found", "Formula", "SOQL"])
    for filename in os.listdir(input_folder):
        if filename.endswith("approvalProcess-meta.xml") and filename.startswith("CoMarketing__c"):
            print(f"Processing file: {filename}")
            filepath = os.path.join(input_folder, filename)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                entry_criteria = root.find(".//sf:entryCriteria/sf:formula", ns)
                if entry_criteria is not None:
                    formula = entry_criteria.text.replace("\n", " ").replace("\t", " ")
                    while "  " in formula:
                        formula = formula.replace("  ", " ")
                    soql = formula_to_soql(formula)
                    writer.writerow([filename, "Yes", formula, soql])
                else:
                    writer.writerow([filename, "No", "", ""])
            except ET.ParseError as e:
                writer.writerow([filename, "Error", str(e), ""])

print(f"Results written to {output_file}")
