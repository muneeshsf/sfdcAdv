import os
import xml.etree.ElementTree as ET
import pandas as pd
import subprocess
import csv
from io import StringIO

# SFDX path and org alias
sf_path = r"C:\Program Files\sf\bin\sf.cmd"  # Update this path
username_alias = "xxxprod"  # Your SFDX org alias

# Set the folder path containing approval process XMLs
input_folder = "C:\\Muneesh\\ApprovalProcesses\\unpackaged\\approvalProcesses"
output_file = "c:\\Muneesh\\Approvers_ReportUserActive.xlsx"

# Verify input folder path
if not os.path.exists(input_folder):
    print(f"❌ Error: Input folder '{input_folder}' does not exist.")
    exit()

if not os.path.isdir(input_folder):
    print(f"❌ Error: '{input_folder}' is not a directory.")
    exit()

# Define namespace
ns = {"sf": "http://soap.sforce.com/2006/04/metadata"}

# List to hold extracted data
data = []
active_user_approvers = set()

# Dictionary to hold approvers for each process
process_approvers = {}

# Fetch IsActive column from User table
query = "SELECT Username, IsActive FROM User"
full_command = f'"{sf_path}" data query --query "{query}" --target-org {username_alias} --result-format csv'
try:
    result = subprocess.run(full_command, capture_output=True, shell=True, check=True)
    output = result.stdout.decode('utf-8', errors='ignore')
    user_data = pd.read_csv(StringIO(output))
    user_table = user_data.set_index('Username')['IsActive'].to_dict()
except Exception as e:
    print(f"❌ Error fetching user data: {str(e)}")
    exit()

# Loop through all XML files in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".approvalProcess"):
        filepath = os.path.join(input_folder, filename)
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            process_name = filename.replace(".approvalProcess", "")
            active = root.findtext("sf:active", default="false", namespaces=ns).lower() == "true"
            steps = root.findall("sf:approvalStep", ns)
            print("Steps : " + str(len(steps)))
            process_approver_names = []
            if not steps:
                data.append({
                    "Approval Process": process_name,
                    "Active": active,
                    "Step": "N/A",
                    "Approver Type": "N/A",
                    "Approver Name": "N/A",
                    "SFDC Active": "N/A"
                })
            else:
                for step in steps:
                    step_name = step.findtext("sf:name", default="UnnamedStep", namespaces=ns)
                    assigned_approvers = step.findall("sf:assignedApprover", ns)
                    print("Step Name : " + step_name)
                    print("Assigned Approvers : " + str(len(assigned_approvers)))
                    for approver_block in assigned_approvers:
                        approvers_xml = approver_block.findall("sf:approver", ns)
                        for approver in approvers_xml:
                            approver_name = approver.findtext("sf:name", default="N/A", namespaces=ns)
                            approver_type = approver.findtext("sf:type", default="Unknown", namespaces=ns)
                            sfdc_active = user_table.get(approver_name, 'Unknown')
                            data.append({
                                "Approval Process": process_name,
                                "Active": active,
                                "Step": step_name,
                                "Approver Type": approver_type,
                                "Approver Name": approver_name,
                                "SFDC Active": sfdc_active
                            })
                            if active and approver_type.lower() == "user":
                                active_user_approvers.add(approver_name)
                                if active:
                                    process_approver_names.append(approver_name)
            if active:
                process_approvers[process_name] = ", ".join(f"'{name}'" for name in set([name for name in process_approver_names if name in active_user_approvers]))
        except ET.ParseError as e:
            print(f"❌ Error parsing {filename}: {str(e)}")

# Create DataFrames
df_data = pd.DataFrame(data)
df_approvers = pd.DataFrame(sorted(list(active_user_approvers)), columns=["Approver Name"])
df_process_approvers = pd.DataFrame([", ".join(f"'{name}'" for name in active_user_approvers)], columns=["Approvers"])

# Write data to Excel file
with pd.ExcelWriter(output_file) as writer:
    df_data.to_excel(writer, sheet_name="Approvers Report", index=False)
    df_approvers.to_excel(writer, sheet_name="Distinct Active User Approvers", index=False)
    df_process_approvers.to_excel(writer, sheet_name="Process Approvers", index=False)

print(f"✅ Approvers report saved to: {output_file}")