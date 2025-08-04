import pandas as pd
import subprocess
import json

# SFDX path and org alias
sf_path = r"C:\Program Files\sf\bin\sf.cmd"  # Update this path
username_alias = "metaprod"  # Your SDFX org alias

# Read the CSV file
csv_file = 'C:\\Muneesh\\CustomSettings\\report.csv'
df = pd.read_csv(csv_file)

# Get unique emails
unique_emails = set()
for index, row in df.iterrows():
    emails = str(row['Value']).replace(" ", "").split(';')
    for email in emails:
        for e in email.split(','):
            unique_emails.add(e.strip().lower())

# Create a single query to retrieve IsActive flag for all unique users
emails_str = "','".join(unique_emails)
query = f"SELECT Email, IsActive FROM User WHERE Email IN ('{emails_str}')"

# Execute the query
command = f"{sf_path} data query --query \"{query}\" --target-org {username_alias} --result-format json"
response = subprocess.run(command, shell=True, capture_output=True, text=True)

# Parse the response
user_results = {}
if response.stdout:
    try:
        response_json = json.loads(response.stdout)
        for record in response_json['result']['records']:
            user_results[record['Email'].lower()] = str(record['IsActive']).lower()
    except Exception as e:
        print(f"Error occurred: {e}")

# Create a new DataFrame with the results
new_df = df.copy()
new_df['Value'] = new_df['Value'].apply(lambda x: [email.strip().lower() for email in str(x).replace(" ", "").split(';')])
new_df = new_df.explode('Value')
new_df['Value'] = new_df['Value'].apply(lambda x: [e.strip().lower() for e in x.split(',')])
new_df = new_df.explode('Value')
new_df['isActive'] = new_df['Value'].apply(lambda x: user_results.get(x, 'User not found'))

# Create separate DataFrames for active users, inactive users, and not found users
active_users_df = new_df[(new_df['isActive'] == 'true')]
inactive_users_df = new_df[(new_df['isActive'] == 'false')]
not_found_users_df = new_df[new_df['isActive'] == 'User not found']

# Save the results to separate CSV files
with pd.ExcelWriter('C:\\Muneesh\\CustomSettings\\final_report.xlsx') as writer:
    active_users_df.to_excel(writer, sheet_name='Active Users', index=False)
    inactive_users_df.to_excel(writer, sheet_name='Inactive Users', index=False)
    not_found_users_df.to_excel(writer, sheet_name='Not Found Users', index=False)
