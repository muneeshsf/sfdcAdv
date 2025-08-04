import os
import csv
import xml.etree.ElementTree as ET
import re
import subprocess
from simple_salesforce import Salesforce

# === CONFIGURATION ===
folder_path = "C:\\Muneesh\\ApprovalProcesses\\unpackaged\\approvalProcesses"
object_api_name = 'CoMarketing__c'
record_id = 'aMw8V000000oOC1SAM'
username_alias = "metaprod"

# === Salesforce Connection ===
def get_access_token(alias):
    result = subprocess.run(['sf', 'org', 'display', '--target-org', alias, '--json'], stdout=subprocess.PIPE)
    import json
    output = json.loads(result.stdout.decode('utf-8'))
    return output['result']['accessToken'], output['result']['instanceUrl']

access_token, instance_url = get_access_token(username_alias)
sf = Salesforce(instance_url=instance_url, session_id=access_token)

# === Fetch Record Dynamically ===
record = sf.__getattr__(object_api_name).get(record_id)

# === Helper Functions ===
def get_filter(field: str, operator: str, value: str):
    return {
        'equals': lambda rec: str(rec.get(field, '')).lower() == value.lower(),
        'notEqual': lambda rec: str(rec.get(field, '')).lower() != value.lower(),
        'greaterThan': lambda rec: float(rec.get(field, 0)) > float(value),
        'lessThan': lambda rec: float(rec.get(field, 0)) < float(value),
        'greaterOrEqual': lambda rec: float(rec.get(field, 0)) >= float(value),
        'lessOrEqual': lambda rec: float(rec.get(field, 0)) <= float(value),
        'contains': lambda rec: value.lower() in str(rec.get(field, '')).lower()
    }.get(operator, lambda rec: False)

def evaluate_boolean_filter(boolean_filter: str, criteria_results):
    expr = boolean_filter
    for i, result in enumerate(criteria_results):
        expr = re.sub(rf'\b{i+1}\b', str(result), expr)
    expr = expr.replace('AND', 'and').replace('OR', 'or')
    try:
        return eval(expr)
    except:
        return False

# === Scan Folder for Matching XMLs ===
matches = []
for file in os.listdir(folder_path):
    if not file.endswith('.xml'):
        continue

    file_path = os.path.join(folder_path, file)
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError:
        continue

    if root.findtext('object') != object_api_name:
        continue

    approval_name = root.findtext('fullName', file.replace('.xml', ''))
    entry_criteria = root.find('entryCriteria')
    if entry_criteria is None:
        continue

    boolean_filter = entry_criteria.findtext('booleanFilter') or ''
    criteria_items = entry_criteria.findall('criteriaItems')

    filters = []
    for item in criteria_items:
        field = item.findtext('field')
        operator = item.findtext('operation')
        value = item.findtext('value')
        if field and operator and value:
            filters.append({
                'field': field,
                'operator': operator,
                'value': value,
                'func': get_filter(field, operator, value)
            })

    individual_results = [f['func'](record) for f in filters]
    is_match = evaluate_boolean_filter(boolean_filter, individual_results) if boolean_filter else all(individual_results)

    if is_match:
        matches.append({
            'Approval Process': approval_name,
            'Record ID': record_id,
            'Matched Fields': ', '.join([f['field'] for f in filters])
        })

# === Write to CSV ===
output_csv = os.path.join(folder_path, f'{object_api_name}_approval_matches.csv')
with open(output_csv, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Approval Process', 'Record ID', 'Matched Fields'])
    writer.writeheader()
    for row in matches:
        writer.writerow(row)

print(f"✅ Match report saved to: {output_csv}")
