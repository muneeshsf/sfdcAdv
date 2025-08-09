import os
import json
import subprocess as sp
import requests
import csv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
ORG_ALIAS = "metaprod"  # Your SFDX org alias
LOG_TYPE = "ApexUnexpectedException"  # Log type to download
TARGET_DIR = "./logs"  # Folder to save the log files
SF_PATH = r"C:\Program Files\sf\bin\sf.cmd"  # Path to sf executable

def run_shell_command(cmd: str) -> str:
    """Run a shell command and return the output."""
    try:
        result = sp.run(cmd, capture_output=True, text=True, shell=True, check=True)
        return result.stdout
    except sp.CalledProcessError as e:
        logging.error(f"Failed to run command: {e}")
        raise

def get_event_log_files(org_alias: str, log_type: str) -> dict:
    """Query for EventLogFile records of the selected type."""
    query = f"SELECT Id, LogFile, EventType, LogDate FROM EventLogFile WHERE EventType = '{log_type}' ORDER BY LogDate DESC"
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
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(target_file, "wb") as f:
        f.write(response.content)
    logging.info(f"Log file downloaded to: {target_file}")

def parse_log_file(input_file: str, output_file: str) -> None:
    """Parse the log file and extract error information."""
    desired_columns = [
        "USER_ID",
        "EXCEPTION_TYPE",
        "EXCEPTION_MESSAGE",
        "STACK_TRACE",
        "EXCEPTION_CATEGORY",
        "TIMESTAMP_DERIVED",
        "USER_ID_DERIVED"
    ]
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f_in, open(output_file, 'w', newline='', encoding='utf-8') as f_out:
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=desired_columns)
            writer.writeheader()
            for row in reader:
                if row.get("EXCEPTION_MESSAGE"):
                    writer.writerow({column: row.get(column, '') for column in desired_columns})
        logging.info(f"Error log file saved to: {output_file}")
    except Exception as e:
        logging.error(f"Failed to parse log file: {e}")
        raise

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    try:
        access_token, instance_url = get_session_token_and_instance_url(ORG_ALIAS)
        query_json = get_event_log_files(ORG_ALIAS, LOG_TYPE)
        if "result" in query_json and "records" in query_json["result"] and len(query_json["result"]["records"]) > 0:
            for record in query_json["result"]["records"]:
                log_file_url = record["LogFile"]
                event_date = record["LogDate"].split("T")[0]

                target_file = os.path.join(TARGET_DIR, f"{LOG_TYPE}_{event_date}.csv")
                download_log_file(instance_url + log_file_url, access_token, target_file)

                error_file = os.path.join(TARGET_DIR, f"{LOG_TYPE}_{event_date}_errors.csv")
                parse_log_file(target_file, error_file)
        else:
            logging.info(f"No records found for {LOG_TYPE}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
