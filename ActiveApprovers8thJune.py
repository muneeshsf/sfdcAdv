import os
import xml.etree.ElementTree as ET
import subprocess
import csv
import xlsxwriter

# SFDX path and org alias
sf_path = r"C:\Program Files\sf\bin\sf.cmd"  # Update this path
username_alias = "metaprod"  # Your SFDX org alias

# Set the folder path containing approval process XMLs
input_folder = "C:\\Muneesh\\ApprovalProcesses\\unpackaged\\approvalProcesses"
output_file = "c:\\Muneesh\\Approvers_ReportActive.xlsx"

# Define namespace
ns = {"sf": "http://soap.sforce.com/2006/04/metadata"}

# List to hold extracted data
data = []
active_user_approvers = set()

# Dictionary to hold approvers for each process
process_approvers = {}

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
                            data.append({
                                "Approval Process": process_name,
                                "Active": active,
                                "Step": step_name,
                                "Approver Type": approver_type,
                                "Approver Name": approver_name,
                                "SFDC Active": "Unknown"
                            })
                            if active and approver_type.lower() == "user":
                                active_user_approvers.add(approver_name)
                                if active:
                                    process_approver_names.append(approver_name)
            if active:
                process_approvers[process_name] = ", ".join(f"'{name}'" for name in set([name for name in process_approver_names if name in active_user_approvers]))
        except ET.ParseError as e:
            print(f"❌ Error parsing {filename}: {str(e)}")

# Fetch IsActive column for active user approvers
if active_user_approvers:
    approver_names = ", ".join(f"'{name}'" for name in active_user_approvers)
    query = f"SELECT Username, IsActive FROM User WHERE Username IN ({approver_names})"
    full_command = f'"{sf_path}" data query --query "{query}" --target-org {username_alias} --result-format csv'
    options = {"capture_output": True, "text": True, "shell": True}
    try:
        result = subprocess.run(full_command, **options)
        user_table = {}
        reader = csv.DictReader(result.stdout.splitlines())
        for row in reader:
            user_table[row['Username']] = row['IsActive']
    except Exception as e:
        print(f"❌ Error fetching user data: {str(e)}")
        exit()

    # Update SFDC Active status in data
    for row in data:
        if row["Approver Name"] in user_table:
            row["SFDC Active"] = user_table[row["Approver Name"]]

# Create DataFrames
workbook = xlsxwriter.Workbook(output_file)
worksheet_data = workbook.add_worksheet("Approvers Report")
worksheet_approvers = workbook.add_worksheet("Distinct Active User Approvers")
worksheet_process_approvers = workbook.add_worksheet("Process Approvers")

# Write data to Excel file
worksheet_data.write_row(0, 0, ["Approval Process", "Active", "Step", "Approver Type", "Approver Name", "SFDC Active"])
for i, row in enumerate(data):
    worksheet_data.write_row(i+1, 0, [row["Approval Process"], row["Active"], row["Step"], row["Approver Type"], row["Approver Name"], row["SFDC Active"]])

worksheet_approvers.write_row(0, 0, ["Approver Name"])
for i, approver in enumerate(sorted(list(active_user_approvers))):
    worksheet_approvers.write_row(i+1, 0, [approver])

worksheet_process_approvers.write_row(0, 0, ["Approvers"])
worksheet_process_approvers.write_row(1, 0, [", ".join(f"'{name}'" for name in active_user_approvers)])

workbook.close()

print(f"✅ Approvers report saved to: {output_file}")
