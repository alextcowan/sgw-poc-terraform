# Chrome Enterprise Security Gateway with Terraform

This repository contains Terraform scripts to deploy a Google Cloud BeyondCorp Security Gateway and associated applications. It provides a baseline for securing access to both a public and private web application.

In addition to the security gateway, it provides firewall rule configuration, and Cloud Storage bucket creation for PAC file hosting.

---
## Prerequisites

* A Google Cloud project with billing enabled.
* Chrome Enterprise Premium licensing enabled on the GCP project
* Allowlisted Private Web Application Security Gateway access (for private webapp access)
* An authenticated Google Cloud Shell environment.
* The Go programming language (this is pre-installed on Cloud Shell).

---
## 1. Set Up the Custom Terraform Provider

These steps compile and install a specific version of the Terraform Google Provider locally. This is required before initializing this project's configuration.

All commands should be run from your Google Cloud Shell terminal.

#### **A. Clone the Provider Source Code**
This command downloads the source code for the Terraform Google Provider.

```bash
git clone https://github.com/hashicorp/terraform-provider-google.git $GOPATH/src/github.com/hashicorp/terraform-provider-google
```

### **B. Build the Provider from Source**
Next, navigate into the directory and compile the provider binary using Go.

```bash
cd $GOPATH/src/github.com/hashicorp/terraform-provider-google
go build -o terraform-provider-google
```

### **C. Install the Local Provider Plugin**
Finally, create the required directory structure and copy the compiled provider into it. Terraform will automatically discover and use this local plugin during initialization.

```bash
cd ~
mkdir -p ~/.terraform.d/plugins/local/hashicorp/google/6.43.0/linux_amd64
cp $GOPATH/src/github.com/hashicorp/terraform-provider-google/terraform-provider-google ~/.terraform.d/plugins/local/hashicorp/google/6.43.0/linux_amd64/
```

With the provider set up, you can now deploy the security gateway infrastructure.

---
## 2. Deploy the Infrastructure

#### **A. Clone this Repository**
Clone this repository into your Cloud Shell environment.

```bash
cd ~
git clone https://github.com/alextcowan/sgw-poc-terraform.git
cd sgw-poc-terraform
```
#### **B. Configure Variables**
Create a `terraform.tfvars` file to define your environment. You can use the `terraform.tfvars.example` file as a reference.

*Example `terraform.tfvars`:*
```hcl
project_id = "your-gcp-project-id"
region     = ["australia-southeast1"]
# ... other variables
```
#### **C. Modify PAC File**
Modify the `const sites` portion of the included sgw-pac.js file to match your hostname matchers.  

*Example `sgw-pac.js`:*
```javascript
function FindProxyForURL(url, host) {
  const PROXY = "HTTPS ingress.cloudproxy.app:443";
  const sites = ["ipify.org", "ipinfo.io", "microsoftonline.com", "onprem.securebrowsing.cloud"]; // add URLs to match all of your CAG app domains

  for (const site of sites) {
    if (shExpMatch(url, 'https://' + site + '/*') || shExpMatch(url, '*.' + site + '/*')) {
      return PROXY;
    }
  }
  return 'DIRECT';
}
```
#### **D. Initialize and Apply**
Initialize Terraform to download the necessary plugins (it will use the local provider you just built) and then apply the configuration to create the resources.

```bash
terraform init
terraform plan
terraform apply
```
Review the plan and type `yes` to proceed.

---
## 3. Cleanup
To remove all resources created by this configuration, run the `destroy` command.

```bash
terraform destroy
```
