#!/usr/bin/env python3
import argparse
import subprocess
import re
import sys
import os
import json
from datetime import datetime

TFVARS_FILE = "terraform.tfvars"
API_ENDPOINT = "beyondcorp.googleapis.com"
API_VERSION = "v1"
SEPARATOR_CHAR = "─"

def strip_emojis(text: str) -> str:
    """Removes emoji characters from a string."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

class TeeLogger:
    """A file-like object that writes to a file and another stream (stdout)."""
    def __init__(self, filename, stream):
        self.stream = stream
        self.logfile = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        self.stream.write(message)
        self.logfile.write(strip_emojis(message))

    def flush(self):
        self.stream.flush()
        self.logfile.flush()
    
    def close(self):
        self.logfile.close()

def parse_tfvars(file_path: str) -> dict:
    """Parses a .tfvars file to extract simple key-value pairs."""
    if not os.path.exists(file_path):
        print(f"❌ Error: '{file_path}' not found in the current directory.")
        sys.exit(1)
    config = {}
    simple_assignment_re = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*=\s*"(.*?)"\s*$')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                match = simple_assignment_re.match(line)
                if match:
                    key, value = match.groups()
                    config[key] = value
    except IOError as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        sys.exit(1)
    return config

def get_gcp_token() -> str:
    """Retrieves a GCP access token using the gcloud CLI."""
    print("🔐 Retrieving GCP access token...")
    try:
        token_process = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        return token_process.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n❌ Error: Failed to get gcloud access token.")
        print("   Please ensure the 'gcloud' CLI is installed and you are authenticated ('gcloud auth login').")
        sys.exit(1)

def make_api_call(url: str, token: str) -> dict:
    """Makes a generic API call and returns the JSON response."""
    command = ["curl", "--silent", "-H", f"Authorization: Bearer {token}", "-H", "Content-Type: application/json", url]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        print(f"❌ API call to '{url}' failed.")
        try:
            error_json = json.loads(e.stdout)
            print(json.dumps(error_json, indent=2))
        except json.JSONDecodeError:
            print(f"   Status Code: {e.returncode}\n   Response: {e.stdout or e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Failed to parse API response from '{url}'.")
        sys.exit(1)

def get_gateway_details(config: dict, token: str):
    """Fetches and displays details for the Security Gateway."""
    project_id, security_gateway_id = config.get("project_id"), config.get("security_gateway_id")
    print(f"\n🔍 Fetching details for Security Gateway '{security_gateway_id}'...")
    url = f"https://{API_ENDPOINT}/{API_VERSION}/projects/{project_id}/locations/global/securityGateways/{security_gateway_id}"
    response_json = make_api_call(url, token)
    print(json.dumps(response_json, indent=2))

def get_application_details(config: dict, token: str):
    """Fetches and displays details for all applications on the gateway."""
    project_id, security_gateway_id = config.get("project_id"), config.get("security_gateway_id")
    print(f"\n🔍 Listing applications for Security Gateway '{security_gateway_id}'...")
    list_url = f"https://{API_ENDPOINT}/{API_VERSION}/projects/{project_id}/locations/global/securityGateways/{security_gateway_id}/applications"
    list_response = make_api_call(list_url, token)
    applications = list_response.get('applications', [])
    if not applications:
        print("ℹ️ No applications found for this Security Gateway.")
        return
    print(f"✅ Found {len(applications)} application(s). Fetching details...\n")
    for i, app in enumerate(applications):
        app_name_path = app.get('name')
        if not app_name_path: continue
        app_id = app_name_path.split('/')[-1]
        detail_url = f"https://{API_ENDPOINT}/{API_VERSION}/{app_name_path}"
        title = f"📄 --- Details for Application: {app_id} ---"
        print(title)
        app_details = make_api_call(detail_url, token)
        print(json.dumps(app_details, indent=2))
        if i < len(applications) - 1:
            print(SEPARATOR_CHAR * len(title) + "\n")

def get_access_policies(config: dict, token: str):
    """Fetches and displays IAM policies for the gateway and its applications."""
    project_id, security_gateway_id = config.get("project_id"), config.get("security_gateway_id")
    gw_iam_url = f"https://{API_ENDPOINT}/{API_VERSION}/projects/{project_id}/locations/global/securityGateways/{security_gateway_id}:getIamPolicy"
    title_gw = f"🔑 --- IAM Policy for Security Gateway: {security_gateway_id} ---"
    print(f"\n{title_gw}")
    gateway_policy = make_api_call(gw_iam_url, token)
    print(json.dumps(gateway_policy, indent=2))
    print(f"\n{SEPARATOR_CHAR * 70}\n")
    print("🔍 Listing applications to fetch their IAM policies...")
    list_url = f"https://{API_ENDPOINT}/{API_VERSION}/projects/{project_id}/locations/global/securityGateways/{security_gateway_id}/applications"
    list_response = make_api_call(list_url, token)
    applications = list_response.get('applications', [])
    if not applications:
        print("ℹ️ No applications found to fetch policies from.")
        return
    print(f"✅ Found {len(applications)} application(s). Fetching policies...\n")
    for i, app in enumerate(applications):
        app_name_path = app.get('name')
        if not app_name_path: continue
        app_id = app_name_path.split('/')[-1]
        app_iam_url = f"https://{API_ENDPOINT}/{API_VERSION}/{app_name_path}:getIamPolicy"
        title_app = f"👤 --- IAM Policy for Application: {app_id} ---"
        print(title_app)
        app_policy = make_api_call(app_iam_url, token)
        print(json.dumps(app_policy, indent=2))
        if i < len(applications) - 1:
            print(f"\n{SEPARATOR_CHAR * len(title_app)}\n")

def show_config_info(config: dict):
    """Displays the necessary configuration info for end-users."""
    required_keys = ["project_id", "security_gateway_id", "bucket_name", "pac_file_path"]
    if not all(key in config for key in required_keys):
        missing = [key for key in required_keys if key not in config]
        print(f"❌ Error: Missing required keys in {TFVARS_FILE}.\n   Ensure the following are defined: {', '.join(missing)}")
        sys.exit(1)
    print("\n🖥️   1. Chrome Extension Configuration")
    print("Instructions: https://cloud.google.com/beyondcorp-enterprise/docs/security-gateway-saas-apps#install-cep-extension")
    print("For the Secure Enterprise Browser extension, copy and paste the following JSON into the policy field:")
    project_id, sgw_id = config["project_id"], config["security_gateway_id"]
    extension_json = { "securityGateway": { "Value": { "authentication": {}, "context": {"resource": f"projects/{project_id}/locations/global/securityGateways/{sgw_id}"}}}}
    print(f"\n{json.dumps(extension_json, indent=2)}\n")
    print(f"{SEPARATOR_CHAR * 70}\n")
    print("🔗  2. Proxy (PAC File) Configuration")
    print("Instructions: https://cloud.google.com/beyondcorp-enterprise/docs/security-gateway-saas-apps#update_the_proxy_mode_settings")
    print("In Chrome proxy mode settings, set 'Automatic proxy configuration' to this URL:")
    bucket_name, pac_file = config["bucket_name"], config["pac_file_path"]
    pac_url = f"https://storage.googleapis.com/{bucket_name}/{pac_file}"
    print(f"\n  {pac_url}\n")

def show_debug_info(config: dict):
    """Displays and logs a comprehensive set of debug information."""
    timestamp = datetime.now().strftime('%Y%d%m-%H-%M-%S')
    log_filename = f"sgw-debug-{timestamp}.txt"
    print(f"📝 Saving debug output to '{log_filename}'...")
    
    original_stdout = sys.stdout
    sys.stdout = TeeLogger(log_filename, original_stdout)

    try:
        print("🚀 Running full debug diagnostic...")
        token = get_gcp_token()
        
        get_gateway_details(config, token)
        print(f"\n{SEPARATOR_CHAR * 70}")
        get_application_details(config, token)
        print(f"\n{SEPARATOR_CHAR * 70}")
        get_access_policies(config, token)

        print(f"\n{SEPARATOR_CHAR * 70}")
        title_pac = "📜 --- PAC File Content ---"
        print(title_pac)
        bucket_name, pac_file = config.get("bucket_name"), config.get("pac_file_path")
        if not all([bucket_name, pac_file]):
            print("ℹ️  Skipping PAC file: 'bucket_name' or 'pac_file_path' not in config.")
            return
        gs_path = f"gs://{bucket_name}/{pac_file}"
        print(f"🔍 Fetching content from '{gs_path}'...\n")
        try:
            command = ["gcloud", "storage", "cat", gs_path]
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            print(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Error: Failed to fetch PAC file from GCS.")
            if isinstance(e, subprocess.CalledProcessError) and e.stderr:
                 print(f"   gcloud stderr: {e.stderr.strip()}")
            else:
                print("   Please ensure the 'gcloud' CLI is installed and authenticated.")
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout

def get_vpc_network_path():
    """Gets the VPC network path for the current project."""
    print("🔍 Determining VPC network path...")
    try:
        # Get the network name
        network_name_cmd = "gcloud compute networks list --format='value(name)'"
        network_name_result = subprocess.run(network_name_cmd, shell=True, check=True, capture_output=True, text=True)
        network_name = network_name_result.stdout.strip()
        if not network_name:
            print("❌ No VPC network found for the current project.")
            sys.exit(1)

        # Describe the network to get the selfLink
        describe_cmd = f"gcloud compute networks describe {network_name} --format='value(selfLink)'"
        describe_result = subprocess.run(describe_cmd, shell=True, check=True, capture_output=True, text=True)
        self_link = describe_result.stdout.strip()

        # Process the URL to get the desired path
        if 'projects/' in self_link:
            network_path = self_link[self_link.find('projects/'):]
            print(f"✅ VPC Network Path: {network_path}")
        else:
            print("❌ Could not parse the VPC network path from gcloud output.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing gcloud command: {e}")
        print(f"   Stderr: {e.stderr.strip()}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

def main():
    """Main function to parse arguments and call the appropriate handler."""
    parser = argparse.ArgumentParser(
        description="A helper script to interact with the Google Cloud Security Gateway API and other project resources.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'command',
        choices=['gateway', 'applications', 'config', 'access', 'debug', 'vpc-network'],
        help="The type of information to display:\n"
             "  gateway      - Show details for the configured Security Gateway.\n"
             "  applications - List and show details for all associated applications.\n"
             "  config       - Show post-creation configuration for the Admin Console.\n"
             "  access       - Show IAM policies for the gateway and all applications.\n"
             "  debug        - Display all details, and PAC file contents.\n"
             "  vpc-network  - Get the full path of the project's VPC network."
    )
    args = parser.parse_args()
    
    if args.command == 'vpc-network':
        get_vpc_network_path()
        return

    config_vars = parse_tfvars(TFVARS_FILE)

    if args.command in ['gateway', 'applications', 'access', 'debug']:
        if not all(k in config_vars for k in ["project_id", "security_gateway_id"]):
            print("❌ Error: 'project_id' and 'security_gateway_id' must be defined in terraform.tfvars.")
            sys.exit(1)

    if args.command == 'config':
        show_config_info(config_vars)
    elif args.command == 'debug':
        show_debug_info(config_vars)
    elif args.command in ['gateway', 'applications', 'access']:
        token = get_gcp_token()
        if args.command == 'gateway':
            get_gateway_details(config_vars, token)
        elif args.command == 'applications':
            get_application_details(config_vars, token)
        elif args.command == 'access':
            get_access_policies(config_vars, token)


if __name__ == "__main__":
    main()
