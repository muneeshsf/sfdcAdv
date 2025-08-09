import os
import xml.etree.ElementTree as ET
import pandas as pd

# === CONFIG ===
input_folder = "C:\\Muneesh\\ApprovalProcesses\\unpackaged\\approvalProcesses"  # Folder with XML files
output_excel = "C:\\Muneesh\\Approval_Process_Approvers.xlsx"

# === PROCESS ===
object_tabs = {}

for file_name in os.listdir(input_folder):
    if file_name.endswith(".approvalProcess"):
        file_path = os.path.join(input_folder, file_name)
        tree = ET.parse(file_path)
        root = tree.getroot()

        ns = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
        object_name = file_name.split('.')[0]  # e.g., Account
        approval_name = root.find('sf:fullName', ns)
        approval_name_text = approval_name.text if approval_name is not None else 'Unknown'

        # Find all step approvers
        steps = root.findall('.//sf:approvalStep', ns)
        for step in steps:
            step_name = step.find('sf:name', ns).text if step.find('sf:name', ns) is not None else 'UnnamedStep'
            assignedTo = step.find('.//sf:assignedApprover/sf:type', ns)
            approverType = assignedTo.text if assignedTo is not None else 'Not Found'

            approverDetails = step.find('.//sf:assignedApprover/sf:name', ns)
            approverName = approverDetails.text if approverDetails is not None else 'N/A'

            row = {
                'Approval Process Name': approval_name_text,
                'Step Name': step_name,
                'Approver Type': approverType,
                'Approver Name': approverName
            }

            if object_name not in object_tabs:
                object_tabs[object_name] = []

            object_tabs[object_name].append(row)

# === WRITE TO EXCEL ===
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    for object_name, rows in object_tabs.items():
        df = pd.DataFrame(rows)
        df.to_excel(writer, sheet_name=object_name[:31], index=False)  # Excel sheet names max 31 chars

print(f"✅ Excel file generated: {output_excel}")
