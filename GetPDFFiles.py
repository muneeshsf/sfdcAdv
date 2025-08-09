import json
import subprocess
import requests
import os

# Salesforce org alias
org_alias = 'metaprod'

# Local folder to save PDF files
folder_path = 'pdf_files'

# Create the folder if it doesn't exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Query PartnerFundClaim records with Approved status
query_partner_fund_claim = "SELECT Id FROM PartnerFundClaim WHERE Status = 'Approved' and BudgetId ='0Cw8V000000wu6MSAQ'"
command_partner_fund_claim = f"sfdx force:data:soql:query --query \"{query_partner_fund_claim}\" --target-org {org_alias} --json"
result_partner_fund_claim = subprocess.run(command_partner_fund_claim, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if result_partner_fund_claim.returncode != 0:
    print(f"Error executing command: {command_partner_fund_claim}")
    print(f"Return code: {result_partner_fund_claim.returncode}")
    print(f"Error message: {result_partner_fund_claim.stderr.decode('utf-8')}")
else:
    try:
        result_partner_fund_claim_json = json.loads(result_partner_fund_claim.stdout.decode('utf-8'))
        partner_fund_claim_records = result_partner_fund_claim_json['result']['records']

        for partner_fund_claim_record in partner_fund_claim_records:
            partner_fund_claim_id = partner_fund_claim_record['Id']

            # Query ContentDocumentLink
            query = f"SELECT ContentDocumentId, ContentDocument.Title FROM ContentDocumentLink WHERE LinkedEntityId = '{partner_fund_claim_id}' AND ContentDocument.FileType = 'PDF'"
            command = f"sfdx force:data:soql:query --query \"{query}\" --target-org {org_alias} --json"
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                print(f"Error executing command: {command}")
                print(f"Return code: {result.returncode}")
                print(f"Error message: {result.stderr.decode('utf-8')}")
            else:
                try:
                    result_json = json.loads(result.stdout.decode('utf-8'))
                    records = result_json['result']['records']

                    for record in records:
                        content_document_id = record['ContentDocumentId']
                        title = record['ContentDocument']['Title']

                        # Query ContentVersion
                        query_version = f"SELECT Id, VersionData FROM ContentVersion WHERE ContentDocumentId = '{content_document_id}' AND IsLatest = true"
                        command_version = f"sfdx force:data:soql:query --query \"{query_version}\" --target-org {org_alias} --json"
                        result_version = subprocess.run(command_version, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                        if result_version.returncode != 0:
                            print(f"Error executing command: {command_version}")
                            print(f"Return code: {result_version.returncode}")
                            print(f"Error message: {result_version.stderr.decode('utf-8')}")
                        else:
                            try:
                                result_version_json = json.loads(result_version.stdout.decode('utf-8'))
                                version_records = result_version_json['result']['records']

                                if version_records and 'VersionData' in version_records[0]:
                                    file_url = version_records[0]['VersionData']

                                    # Login to Salesforce and get the session ID
                                    command_login = f"sfdx force:org:display --target-org {org_alias} --json"
                                    result_login = subprocess.run(command_login, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    result_login_json = json.loads(result_login.stdout.decode('utf-8'))
                                    access_token = result_login_json['result']['accessToken']
                                    instance_url = result_login_json['result']['instanceUrl']

                                    # Download the file data
                                    headers = {'Authorization': f'Bearer {access_token}'}
                                    response = requests.get(f"{instance_url}{file_url}", headers=headers)

                                    if response.status_code == 200:
                                        # Save the PDF file to the local folder
                                        file_path = os.path.join(folder_path, f'{title}.pdf')
                                        with open(file_path, 'wb') as f:
                                            f.write(response.content)

                                        print(f'Saved PDF file: {title}.pdf')
                                    else:
                                        print(f"Error downloading file: {response.status_code}")
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON: {e}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
