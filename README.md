# Chrome Enterprise Security Gateway with Terraform

This repository contains Terraform scripts to deploy a Google Cloud Chrome Enterprise Premium Security Gateway and associated applications. It provides a baseline for securing access to both a public and private web application.

In addition to the Security Gateway, it provides firewall rule configuration, and Cloud Storage bucket creation for PAC file hosting.

---
## Prerequisites

* A Google Cloud project with billing enabled.
* Chrome Enterprise Premium licensing enabled on the GCP project
* Allowlisted Private Web Application Security Gateway access (for private webapp access)
* An authenticated Google Cloud Shell environment.
* The Go programming language (this is pre-installed on Cloud Shell).

---
## 1. Set Up the custom terraform provider

These steps compile and install a specific version of the Terraform Google Provider locally. This is required before initializing this project's configuration.

All commands should be run from your Google Cloud Shell terminal.

#### **A. Clone the provider source code**
This command downloads the source code for the terraform Google provider.

```bash
git clone https://github.com/hashicorp/terraform-provider-google.git $GOPATH/src/github.com/hashicorp/terraform-provider-google
```

#### **B. Build the provider from Source**
Next, navigate into the directory and compile the provider binary using Go.

```bash
cd $GOPATH/src/github.com/hashicorp/terraform-provider-google
go build -o terraform-provider-google
```

#### **C. Install the local provider plugin**
Finally, create the required directory structure and copy the compiled provider into it. Terraform will automatically discover and use this local plugin during initialization.

```bash
cd ~
mkdir -p ~/.terraform.d/plugins/local/hashicorp/google/6.43.0/linux_amd64
cp $GOPATH/src/github.com/hashicorp/terraform-provider-google/terraform-provider-google ~/.terraform.d/plugins/local/hashicorp/google/6.43.0/linux_amd64/
```

With the provider set up, you can now deploy the security gateway infrastructure.

---
## 2. Deploy the infrastructure

#### **A. Clone this repository**
Clone this repository into your Cloud Shell environment.

```bash
cd ~
git clone https://github.com/alextcowan/sgw-poc-terraform.git
cd sgw-poc-terraform
```
#### **B. Configure variables**
Create a `terraform.tfvars` file to define your environment. You can use the `terraform.tfvars.example` file as a reference.

*Example `terraform.tfvars`:*
```hcl
project_id = "your-gcp-project-id"
region     = ["australia-southeast1"]
# ... other variables
```
#### **C. Initialize and apply**
Initialize terraform to download the necessary plugins (it will use the local provider you just built) and then apply the configuration to create the resources.

```bash
terraform init
terraform plan
terraform apply
```
Review the plan and type `yes` to proceed.

---
## 3. Chrome Configuration
The admin will need to configure Chrome to leverage proxy mode via the Security Gateway and deployment of the Chrome Enterprise Premium extension.

[Configure Google Chrome proxy mode](https://cloud.google.com/beyondcorp-enterprise/docs/security-gateway-saas-apps#configure-chrome-proxy)

[Install the Chrome Enterprise Premium extension](https://cloud.google.com/beyondcorp-enterprise/docs/security-gateway-saas-apps#install-cep-extension)

---
## 4. Cleanup
To remove all resources created by this configuration, run the `destroy` command.

```bash
terraform destroy
```
