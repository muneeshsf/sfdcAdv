import subprocess
import json
import argparse
import os

# === CONFIG ===
sfdx_path = "sf"  # Use sf instead of sfdx
output_dir = os.getcwd()
output_file = os.path.join(output_dir, "retrieve_commands.txt")

parser = argparse.ArgumentParser(description='Generate SFDX retrieve commands')
parser.add_argument('org_alias', nargs='?', default=None, help='Connected SFDX org alias')
args = parser.parse_args()

if args.org_alias is None:
    args.org_alias = input("Enter the org alias: ")

# Get list of metadata types
metadata_types = ["ApexClass", "ApexTrigger", "ApexPage", "AuraDefinitionBundle", "LightningComponentBundle", "Flow", "NamedCredential", "CustomObject", "CustomField", "CustomLabel", "Layout", "Profile", "PermissionSet", "ReportType", "Dashboard", "Report"]

# Generate retrieve commands for each metadata type
retrieve_commands = []
for metadata_type in metadata_types:
    retrieve_commands.append(f"{sfdx_path} project retrieve start -m {metadata_type}:* -o {args.org_alias}")

# === Output Commands ===
print(f"\n{len(retrieve_commands)} retrieve commands generated. Writing to {output_file}...")

with open(output_file, "w") as f:
    for i, cmd in enumerate(retrieve_commands, 1):
        f.write(f"# Command {i}:\n{cmd}\n\n")

print(f"Commands written to {output_file} successfully!")
