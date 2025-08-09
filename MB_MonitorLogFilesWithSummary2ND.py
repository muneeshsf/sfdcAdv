import os
import json
import subprocess as sp
import requests
import csv
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
ORG_ALIAS = "metaprod"  # Your SFDX org alias
#LOG_TYPES = ["API"]  # List of log types to monitor
LOG_TYPES = ["API","ApiTotalUsage", "ApexSoap","BulkApi","BulkApiRequest","BulkApi2" ]  # List of log types to monitor
TARGET_DIR = "./logs"  # Folder to save the log file
SF_PATH = r"C:\Program Files\sf\bin\sf.cmd"  # Path to sf executable

def run_shell_command(cmd: str) -> str:
    """Run a shell command and return the output."""
    try:
        result = sp.run(cmd, capture_output=True, text=True, shell=True, check=True)
        return result.stdout
    except sp.CalledProcessError as e:
        logging.error(f"Failed to run command: {e}")
        raise

def get_latest_log_file(org_alias: str, log_type: str) -> dict:
    """Query for the latest EventLogFile of the selected type."""
    query = f"SELECT Id, LogFile, EventType, LogDate FROM EventLogFile WHERE EventType = '{log_type}' ORDER BY LogDate DESC LIMIT 1"
    query_cmd = f"\"{SF_PATH}\" data query --query \"{query}\" --target-org {org_alias} --json"
    query_result = run_shell_command(query_cmd)
    return json.loads(query_result)

def get_session_token_and_instance_url(org_alias: str) -> tuple:
    """Get session token and instance URL."""
    auth_cmd = f"\"{SF_PATH}\" org display --target-org {org_alias} --json"
    auth_result = run_shell_command(auth_cmd)
    auth_json = json.loads(auth_result)
    return auth_json["result"]["accessToken"], auth_json["result"]["instanceUrl"]

def download_log_file(url: str, access_token: str, target_file: str) -> None:
    """Download the log file using requests."""
    if os.path.exists(target_file):
        logging.info(f"Log file already exists: {target_file}")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(target_file, "wb") as f:
        f.write(response.content)
    logging.info(f"Log file downloaded to: {target_file}")

def parse_log_file(input_file: str, output_file: str, log_type: str) -> str:
    """Parse the log file and extract desired columns."""
    desired_columns = ["USER_ID", "API_TYPE","CLIENT_ID","API_FAMILY", "API_VERSION", "API_RESOURCE","URI ","CLIENT_NAME", "HTTP_METHOD", "CLIENT_IP", "METHOD_NAME","COUNTS_AGAINST_API_LIMIT", "ENTITY_NAME", "CONNECTED_APP_ID ","CONNECTED_APP_NAME", "USER_NAME", "COUNT"]
    try:
        with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=desired_columns)
            writer.writeheader()
            for i, row in enumerate(reader):
                try:
                    api_version = float(row.get("API_VERSION", 0))
                    if api_version < 31:
                        row["COUNT"] = "1"
                        logging.info(f"Row {i+1}: {row}")
                        writer.writerow({column: row.get(column, '') for column in desired_columns})
                except ValueError:
                    pass
        logging.info(f"Filtered log file saved to: {output_file}")
        return output_file
    except Exception as e:
        logging.error(f"Failed to parse log file: {e}")
        raise

def generate_summary(input_file: str, output_file: str) -> None:
    """Generate summary from output file."""
    try:
        summary = {}
        with open(input_file, 'r') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                key = (row["USER_ID"], row["API_FAMILY"], row["API_VERSION"], row["API_RESOURCE"], row["CLIENT_NAME"], row["HTTP_METHOD"], row["ENTITY_NAME"], row["CONNECTED_APP_NAME"], row["USER_NAME"])
                if key in summary:
                    summary[key]["COUNT"] += int(row["COUNT"])
                else:
                    summary[key] = {
                        "USER_ID": row["USER_ID"],
                        "API_FAMILY": row["API_FAMILY"],
                        "API_VERSION": row["API_VERSION"],
                        "API_RESOURCE": row["API_RESOURCE"],
                        "CLIENT_NAME": row["CLIENT_NAME"],
                        "HTTP_METHOD": row["HTTP_METHOD"],
                        "ENTITY_NAME": row["ENTITY_NAME"],
                        "CONNECTED_APP_NAME": row["CONNECTED_APP_NAME"],
                        "USER_NAME": row["USER_NAME"],
                        "COUNT": int(row["COUNT"])
                    }

        with open(output_file, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=["USER_ID", "API_FAMILY", "API_VERSION", "API_RESOURCE", "CLIENT_NAME", "HTTP_METHOD", "ENTITY_NAME", "CONNECTED_APP_NAME", "USER_NAME", "COUNT"])
            writer.writeheader()
            for key, value in summary.items():
                writer.writerow(value)
        logging.info(f"Summary saved to: {output_file}")
    except Exception as e:
        logging.error(f"Failed to generate summary: {e}")
        raise

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
                output_filename = os.path.join(TARGET_DIR, f"{log_type}_{event_date}_output2.csv")
                parsed_file = parse_log_file(input_filename, output_filename, log_type)

                # Generate summary
                summary_filename = os.path.join(TARGET_DIR, f"{log_type}_{event_date}_output_summary2.csv")
                generate_summary(parsed_file, summary_filename)
            else:
                logging.info(f"No records found for {log_type}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
