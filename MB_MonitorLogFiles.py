import os
import json
import subprocess as sp
import requests
import csv
from datetime import datetime

# Configuration
ORG_ALIAS = "metaprod"  # Your SFDX org alias
LOG_TYPES = ["API","ApiTotal", "ApexSoap","BulkApi","BulkApiRequest","BulkApi2" ]  # List of log types to monitor
#LOG_TYPES = ["API"]  # List of log types to monitor
#LOG_TYPES = ["ApiTotalUsage","ApexCallout", "ApexExecution","ApexRestApi","ApexSoap","BulkApi","BulkApiRequest","BulkApi2"]
#LOG_TYPES = ["API","Api Total Usage", ""RestApi"","Apex Callout", "Apex Execution", "Apex REST API","Apex SOAP","Bulk API","Bulk API 2.0", "Bulk API Request"]  # List of log types to monitor
TARGET_DIR = "./logs"  # Folder to save the log file
SF_PATH = r"C:\Program Files\sf\bin\sf.cmd"  # Path to sf executable

def get_latest_log_file(org_alias, log_type):
    """Query for the latest EventLogFile of the selected type"""
    query = f"SELECT Id, LogFile, EventType, LogDate FROM EventLogFile WHERE EventType = '{log_type}' ORDER BY LogDate DESC LIMIT 1"
    query_cmd = f"\"{SF_PATH}\" data query --query \"{query}\" --target-org {org_alias} --json"
    query_result = sp.run(query_cmd, capture_output=True, text=True, shell=True)
    if query_result.returncode != 0:
        print(f"Error running query: {query_result.stderr}")
        raise sp.CalledProcessError(query_result.returncode, query_cmd)
    return json.loads(query_result.stdout)

def get_session_token_and_instance_url(org_alias):
    """Get session token and instance URL"""
    auth_cmd = f"\"{SF_PATH}\" org display --target-org {org_alias} --json"
    auth_result = sp.run(auth_cmd, capture_output=True, text=True, shell=True)
    if auth_result.returncode != 0:
        print(f"Error getting session token: {auth_result.stderr}")
        raise sp.CalledProcessError(auth_result.returncode, auth_cmd)
    auth_json = json.loads(auth_result.stdout)
    return auth_json["result"]["accessToken"], auth_json["result"]["instanceUrl"]

def download_log_file(url, access_token, target_file):
    """Download the log file using requests"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(target_file, "wb") as f:
        f.write(response.content)
    print(f"Log file downloaded to: {target_file}")

def parse_log_file(input_file, output_file, log_type):
    """Parse the log file and extract desired columns"""
    desired_columns = ["LogType", "EventType", "USER_ID_DERIVED", "API_VERSION","API_RESOURCE","CLIENT_NAME","METHOD_NAME","ENTITY_NAME","USER_NAME"]
    with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=desired_columns)
        writer.writeheader()
        for i, row in enumerate(reader):
            try:
                api_version = float(row.get("API_VERSION", 0))
                if api_version < 31:
                    row["LogType"] = log_type
                    row["EventType"] = row.get("EVENT_TYPE", '')
                    print(f"Row {i+1}: {row}")
                    writer.writerow({column: row.get(column, '') for column in desired_columns})
            except ValueError:
                pass
    print(f"Filtered log file saved to: {output_file}")

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    try:
        access_token, instance_url = get_session_token_and_instance_url(ORG_ALIAS)
        for log_type in LOG_TYPES:
            # Query for latest EventLogFile
            query_json = get_latest_log_file(ORG_ALIAS, log_type)
            if "result" in query_json and "records" in query_json["result"] and len(query_json["result"]["records"]) > 0:
                record = query_json["result"]["records"][0]
                log_id = record["Id"]
                log_file_url = record["LogFile"]
                event_date = record["LogDate"].split("T")[0]

                # Download the log file
                input_filename = os.path.join(TARGET_DIR, f"{log_type}_{event_date}_input.csv")
                download_log_file(instance_url + log_file_url, access_token, input_filename)

                # Parse the log file
                output_filename = os.path.join(TARGET_DIR, f"{log_type}_{event_date}_output.csv")
                parse_log_file(input_filename, output_filename, log_type)
            else:
                print(f"No records found for {log_type}")

    except sp.CalledProcessError as e:
        print(f"Failed to run sf command: {e}")
    except requests.RequestException as e:
        print(f"Failed to download log file: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
