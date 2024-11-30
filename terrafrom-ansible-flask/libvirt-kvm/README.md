# Intro

Hi, in this post, we will use [Libvirt](https://libvirt.org/) with [Terraform](https://developer.hashicorp.com/terraform?product_intent=terraform) to provision 2 KVM locally and after that, we will Deploy Flask App & PostgreSQL using [Ansible](https://www.ansible.com).

## Requirements

I used Ubuntu 22.04 LTS as the OS for this project. If you're using a different OS, please make the necessary adjustments when installing the required dependencies.

### Install Terraform

```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform -y
```

Verify installation:

```bash
$ terraform version

Terraform v1.9.8
on linux_amd64
```

### Install Ansible

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y
```

Verify installation:

```bash
$ ansible --version

ansible [core 2.15.1]
...
```

## Create KVM
we will use the [libvirt provider] with Terraform to deploy a KVM Virtual Machine

## Create Ansible Playbook
