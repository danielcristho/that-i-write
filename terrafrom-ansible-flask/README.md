Originally published at: [my personal blog](https://danielcristho.site/blog/automating-flask-and-postgres-using-terraform-ansible) & [dev.to](https://dev.to/danielcristho/provisioning-flask-and-postgresql-on-kvm-with-terraform-and-ansible-55kn)
## 😀 Intro

Hi, in this post, we will use [Libvirt](https://libvirt.org/) with [Terraform](https://developer.hashicorp.com/terraform?product_intent=terraform) to provision 2 KVM locally and after that, we will Deploy Flask App & PostgreSQL using [Ansible](https://www.ansible.com).

## Content

- [Project Architecture](#-project-architecture)
- [Requirements](#-requirements)
- [Create KVM](#create-kvm)
- [Create Ansible Playbook](#create-ansible-playbook)
  - [Playbook to install Docker](#playbook-to-install-docker)
  - [Playbook to install and configure postgresql](#playbook-to-install-and-configure-postgresql)
  - [Playbook to deploy Flask App](#playbook-to-deploy-flask-app)
  - [Run Playbook and testing](#run-playbook-and-testing)
- [Conclusion](#conclusion)

## 📝 Project Architecture

So we will create 2 VMs using Terraform, then deploying a flask project and the database using Ansible.

![Project Architecture](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3raxzmnthm5w24cbfct3.png)

## 🔨 Requirements

I used Ubuntu 22.04 LTS as the OS for this project. If you're using a different OS, please make the necessary adjustments when installing the required dependencies.

The major pre-requisite for this setup is `KVM hypervisor`. So you need to install KVM in your system. If you use Ubuntu you can follow this step:

```bash
sudo apt -y install bridge-utils cpu-checker libvirt-clients libvirt-daemon qemu qemu-kvm
```

Execute the following command to make sure your processor supports virtualisation capabilities:

```bash
$ kvm-ok

INFO: /dev/kvm exists
KVM acceleration can be used
```

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

we will use the [libvirt provider](https://github.com/dmacvicar/terraform-provider-libvirt) with Terraform to deploy a KVM Virtual Machine.

Create `main.tf`, just specify the provider and version you want to use:

```tf
terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
      version = "0.8.1"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

```

Thereafter, run terraform init command to initialize the environment:

```tf
$ terraform init

Initializing the backend...
Initializing provider plugins...
- Reusing previous version of hashicorp/template from the dependency lock file
- Reusing previous version of dmacvicar/libvirt from the dependency lock file
- Reusing previous version of hashicorp/null from the dependency lock file
- Using previously-installed hashicorp/template v2.2.0
- Using previously-installed dmacvicar/libvirt v0.8.1
- Using previously-installed hashicorp/null v3.2.3

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

Now create our `variables.tf`. This `variables.tf` file defines inputs for the libvirt disk pool path, the Ubuntu 20.04 image URL as OS for the VMs , and a list of VM hostnames.

```tf
variable "libvirt_disk_path" {
  description = "path for libvirt pool"
  default     = "default"
}

variable "ubuntu_20_img_url" {
  description = "ubuntu 20.04 image"
  default     = "https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64.img"
}

variable "vm_hostnames" {
  description = "List of VM hostnames"
  default     = ["vm1", "vm2"]
}
```

Let's update our `main.tf`:

```tf
resource "null_resource" "cache_image" {
  provisioner "local-exec" {
    command = "wget -O /tmp/ubuntu-20.04.qcow2 ${var.ubuntu_20_img_url}"
  }
}

resource "libvirt_volume" "base" {
  name   = "base.qcow2"
  source = "/tmp/ubuntu-20.04.qcow2"
  pool   = var.libvirt_disk_path
  format = "qcow2"
  depends_on = [null_resource.cache_image]
}

resource "libvirt_volume" "ubuntu20-qcow2" {
  count          = length(var.vm_hostnames)
  name           = "ubuntu20-${count.index}.qcow2"
  base_volume_id = libvirt_volume.base.id
  pool           = var.libvirt_disk_path
  size           = 10737418240  # 10GB
}

data "template_file" "user_data" {
  count    = length(var.vm_hostnames)
  template = file("${path.module}/config/cloud_init.yml")
}

data "template_file" "network_config" {
  count    = length(var.vm_hostnames)
  template = file("${path.module}/config/network_config.yml")
}

resource "libvirt_cloudinit_disk" "commoninit" {
  count          = length(var.vm_hostnames)
  name           = "commoninit-${count.index}.iso"
  user_data      = data.template_file.user_data[count.index].rendered
  network_config = data.template_file.network_config[count.index].rendered
  pool           = var.libvirt_disk_path
}

resource "libvirt_domain" "domain-ubuntu" {
  count  = length(var.vm_hostnames)
  name   = var.vm_hostnames[count.index]
  memory = "1024"
  vcpu   = 1

  cloudinit = libvirt_cloudinit_disk.commoninit[count.index].id

  network_interface {
    network_name   = "default"
    wait_for_lease = true
    hostname       = var.vm_hostnames[count.index]
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "1"
  }

  disk {
    volume_id = libvirt_volume.ubuntu20-qcow2[count.index].id
  }

  graphics {
    type        = "spice"
    listen_type = "address"
    autoport    = true
  }
}
```

the script will provisions multiple KVM VMs using the Libvirt provider. It downloads an Ubuntu 20.04 base image, clones it for each VM, configures cloud-init for user and network settings, and deploys VMs with specified hostnames, 1GB memory, and SPICE graphics. The setup dynamically adapts based on the number of hostnames provided in var.vm_hostnames.

As I've mentioned, I'm using cloud-init, so lets setup the network config and cloud init under the `config` directory:

```bash
mkdir config/
```

Then create our `config/cloud_init.yml`, just make sure that you configure your public ssh key for ssh access in the config:

```yml
#cloud-config
runcmd:
  - sed -i '/PermitRootLogin/d' /etc/ssh/sshd_config
  - echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
  - systemctl restart sshd
ssh_pwauth: true
disable_root: false
chpasswd:
  list: |
    root:cloudy24
  expire: false
users:
  - name: ubuntu
    gecos: ubuntu
    groups:
      - sudo
    sudo:
      - ALL=(ALL) NOPASSWD:ALL
    home: /home/ubuntu
    shell: /bin/bash
    lock_passwd: false
    ssh_authorized_keys:
      - ssh-rsa AAAA...
```

And then network config, in `config/network_config.yml`:

```yml
version: 2
ethernets:
  ens3:
    dhcp4: true
```

Our project structure should look like this:

```bash
$ tree
.
├── config
│   ├── cloud_init.yml
│   └── network_config.yml
├── main.tf
└── variables.tf
```

Now run a plan, to see what will be done:

```bash
$  terraform plan

data.template_file.user_data[1]: Reading...
data.template_file.user_data[0]: Reading...
data.template_file.network_config[1]: Reading...
data.template_file.network_config[0]: Reading...
...

Plan: 8 to add, 0 to change, 0 to destroy
```

And run `terraform apply` to run our deployment:

```tf
$ terraform apply

...
null_resource.cache_image: Creation complete after 10m36s [id=4239391010009470471]
libvirt_volume.base: Creating...
libvirt_volume.base: Creation complete after 3s [id=/var/lib/libvirt/images/base.qcow2]
libvirt_volume.ubuntu20-qcow2[1]: Creating...
libvirt_volume.ubuntu20-qcow2[0]: Creating...
libvirt_volume.ubuntu20-qcow2[1]: Creation complete after 0s [id=/var/lib/libvirt/images/ubuntu20-1.qcow2]
libvirt_volume.ubuntu20-qcow2[0]: Creation complete after 0s [id=/var/lib/libvirt/images/ubuntu20-0.qcow2]
libvirt_domain.domain-ubuntu[1]: Creating...
...

libvirt_domain.domain-ubuntu[1]: Creation complete after 51s [id=6221f782-48b7-49a4-9eb9-fc92970f06a2]

Apply complete! Resources: 8 added, 0 changed, 0 destroyed
```

Verify VM creation using `virsh` command:

```bash
$ virsh list

 Id   Name   State
----------------------
 1    vm1    running
 2    vm2    running
```

Get instances IP address:

```bash
$ virsh net-dhcp-leases --network default

Expiry Time           MAC address         Protocol   IP address          Hostname   Client ID or DUID
-----------------------------------------------------------------------------------------------------------------------------------------------
2024-12-09 19:50:00   52:54:00:2e:0e:86   ipv4       192.168.122.19/24   vm1        ff:b5:5e:67:ff:00:02:00:00:ab:11:b0:43:6a:d8:bc:16:30:0d
2024-12-09 19:50:00   52:54:00:86:d4:ca   ipv4       192.168.122.15/24   vm2        ff:b5:5e:67:ff:00:02:00:00:ab:11:39:24:8c:4a:7e:6a:dd:78
```

Try to access the vm using `ubuntu` user:

```bash
$ ssh ubuntu@192.168.122.15

The authenticity of host '192.168.122.15 (192.168.122.15)' can't be established.
ED25519 key fingerprint is SHA256:Y20zaCcrlOZvPTP+/qLLHc7vJIOca7QjTinsz9Bj6sk.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.122.15' (ED25519) to the list of known hosts.
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-200-generic x86_64)
...

ubuntu@ubuntu:~$
```

## Create Ansible Playbook

Now let's create the Ansible Playbook to deploy Flask & Postgresql on Docker. First you need to create `ansible` directory and `ansible.cfg` file:

```bash
$ mkdir ansible && cd ansible
```

```bash
[defaults]
inventory = hosts
host_key_checking = True
deprecation_warnings = False
collections = ansible.posix, community.general, community.postgresql
```

Then create inventory file called `hosts`:

```bash
[vm1]
192.168.122.19 ansible_user=ubuntu

[vm2]
192.168.122.15 ansible_user=ubuntu
```

checking our VMs using `ansible ping` command:

```bash
$ ansible -m ping all

192.168.122.15 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
192.168.122.19 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Now create `playbook.yml` and `roles`, this playbook will install and configure Docker, Flask and PostgreSQL:

```bash
---
- name: Deploy Flask
  hosts: vm1
  become: true
  remote_user: ubuntu
  roles:
    - flask
    - config

- name: Deploy Postgresql
  hosts: vm2
  become: true
  remote_user: ubuntu
  roles:
    - psql
    - config
```

### Playbook to install Docker

Now create new directory called `roles/docker`:

```bash
$ mkdir roles
$ mkdir docker
```

Create a new directory in `docker` called `tasks`, then create new file `main.yml`. This file will install Docker & Docker Compose:

```bash
$ mkdir docker/tasks
$ vim main.yml
```

```yml
---
- name: Run update
  ansible.builtin.apt:
    name: aptitude
    state: latest
    update_cache: true

- name: Install dependencies
  ansible.builtin.apt:
    name:
      - net-tools
      - apt-transport-https
      - ca-certificates
      - curl
      - software-properties-common
      - python3-pip
      - virtualenv
      - python3-setuptools
      - gnupg-agent
      - autoconf
      - dpkg-dev
      - file
      - g++
      - gcc
      - libc-dev
      - make
      - pkg-config
      - re2c
      - wget
    state: present
    update_cache: true

- name: Add Docker GPG apt Key
  ansible.builtin.apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    state: present

- name: Add repository into sources list
  ansible.builtin.apt_repository:
    repo: deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_lsb.codename }} stable
    state: present
    filename: docker

- name: Install Docker
  ansible.builtin.apt:
    name:
      - docker-ce
      - docker-ce-cli
    state: present
    update_cache: true

- name: Add non-root to docker group
  user:
    name: ubuntu
    groups: [docker]
    append: true

- name: Install Docker module for Python
  ansible.builtin.pip:
    name: docker

- name: Install Docker-Compose
  ansible.builtin.get_url:
    url: https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64
    dest: /usr/local/bin/docker-compose
    mode: '755'

- name: Create Docker-Compose symlink
  ansible.builtin.command:
    cmd: ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
    creates: /usr/bin/docker-compose

- name: Restart Docker
  ansible.builtin.service:
    name: docker
    state: restarted
    enabled: true
```

### Playbook to install and configure postgresql

Then create new directory called `psql`, create subdirectory called `vars`, `tempalates` & `tasks`:

```bash
$ mkdir psql
$ mkdir psql/vars
$ mkdir psql/templates
$ mkdir psql/tasks
```

After that, in `vars`, create `main.yml`. These are variables used to set username, passwords, etc:

```yml
---
db_port: 5433
db_user: admin
db_password: dbPassword
db_name: todo
```

Next, we will create jinja file called `docker-compose.yml.j2`. With this file we will create postgresql container:

```yml
version: '3.7'
services:
  postgres:
      image: postgres:13
      container_name: db
      restart: unless-stopped
      ports:
        - {{ db_port }}:5432
      networks:
        - flask_network
      environment:
        - POSTGRES_USER={{ db_user }}
        - POSTGRES_PASSWORD={{ db_password }}
        - POSTGRES_DB={{ db_name }}
      volumes:
        - postgres_data:/var/lib/postgresql/data
networks:
  flask_network:

volumes:
  postgres_data:
```

Next, create `main.yml` to `tasks`. So we will copy `docker-compose.yml.j2` and run using `docker compose`:

```yml
---
- name: Add Postgresql Compose
  ansible.builtin.template:
    src: docker-compose.yml.j2
    dest: /home/ubuntu/docker-compose.yml
    mode: preserve

- name: Docker-compose up
  ansible.builtin.shell: docker-compose up -d --build
  args:
    chdir: /home/ubuntu
```

### Playbook to deploy Flask App

First, you need to create directory called `flask`, then create sub-directory again:

```bash
$ mkdir flask
$ mkdir flask/vars
$ mkdir flask/templates
$ mkdir flask/tasks
```

Next, add `main.yml` to `vars`. This file refer to posgtresql variable before, with addition IP address of VM2(database VM):

```yml
---
db_port: 5433
db_user: admin
db_password: dbPassword
db_name: todo
db_host:  192.168.122.15
```

Next, create `config.py.j2` to `templates`. This file will replace the old config file from Flask project:

```jinja
DEV_DB = 'sqlite:///task.db'

pg_user = "{{ db_user }}"
pg_pass = "{{ db_password }}"
pg_db = "{{ db_name }}"
pg_port = {{ db_port }}
pg_host = "{{ db_host }}"

PROD_DB = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
```

Next, create `docker-compose.yml.j2` to templates. With this file we will create a container using `docker compose`:

```yml
version: '3.7'
services:
  flask:
     build: flask
     container_name: app
     restart: unless-stopped
     ports:
       - 5000:5000
     environment:
       - DEBUG=0
     networks:
       - flask_network

networks:
  flask_network:
```

Next, create `main.yml` in `tasks`. With this file we will clone [flask project](https://github.com/danielcristho/Flask_TODO/tree/master), add compose file, replace config.py and create new container using `docker compose`:

```yml
---
- name: Clone html project
  changed_when: false
  ansible.builtin.git:
    repo: https://github.com/danielcristho/Flask_TODO.git
    dest: /home/ubuntu/Flask_TODO
    clone: true

- name: Add Flask Compose
  ansible.builtin.template:
    src: docker-compose.yml.j2
    dest: /home/ubuntu/Flask_TODO/docker-compose.yml
    mode: preserve

- name: Update config.py
  ansible.builtin.template:
    src: config.py.j2
    dest: /home/ubuntu/Flask_TODO/flask/app/config.py
    mode: preserve

- name: Run docker-compose up -d
  shell: docker-compose up -d --build
  args:
    chdir: /home/ubuntu/Flask_TODO
```

Our project structure should look like this:

```bash
├── ansible-flask-psql
│   ├── ansible.cfg
│   ├── hosts
│   ├── playbook.yml
│   └── roles
│       ├── docker
│       │   └── tasks
│       │       └── main.yml
│       ├── flask
│       │   ├── tasks
│       │   │   └── main.yml
│       │   ├── templates
│       │   │   ├── config.py.j2
│       │   │   └── docker-compose.yml.j2
│       │   └── vars
│       │       └── main.yml
│       └── psql
│           ├── tasks
│           │   └── main.yml
│           ├── templates
│           │   └── docker-compose.yml.j2
│           └── vars
│               └── main.yml
├── libvirt-kvm
│   ├── config
│   │   ├── cloud_init.yml
│   │   └── network_config.yml
│   ├── main.tf
│   ├── variables.tf
```

### Run Playbook and testing

Finally, let's run `ansible-playbook` to deploy PostgreSQL and Flask:

```bash
$ ls
ansible.cfg  hosts  playbook.yml  roles

$ ansible-playbook -i host playbook.yml

 _____________________
< PLAY [Deploy Flask] >
 ---------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

 ________________________
< TASK [Gathering Facts] >
 ------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     |
...
 ____________
< PLAY RECAP >
 ------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

192.168.122.15             : ok=13   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
192.168.122.19             : ok=15   changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

After complete, just make sure there is no error. Then you see there are two containers created. In VM1 is Flask and VM2 is Postgresql:

```bash
$ docker ps

CONTAINER ID   IMAGE              COMMAND           CREATED              STATUS              PORTS
                   NAMES
f3978427e34c   flask_todo_flask   "python run.py"   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp, :
::5000->5000/tcp   app

$ docker ps

fbebdff75a6e   postgres:13   "docker-entrypoint.s…"   4 minutes ago   Up 4 minutes   0.0.0.0:5433->5432/tcp, [::]:5433
->5432/tcp   db
```

Try to access the app using browsers, just type `http://<vm1_ip>`:

![Access flask app using browser](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/1qhj7xncpz46dr6cbnwf.png)

Try to add a new task and then the data will be added to the database:

![pgsql content](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/sjckusvrpjlav6z20cx9.png)

#### Conclusion

Finally we have created 2 VMs and deploy Flask Project with database.

Thank you for reading this article. Feel free to leave a comment if you have any questions, suggestions, or feedback.

Nb: Project Repo: Project Repo: [danielcristho/that-i-write/terrafrom-ansible-flask](https://github.com/danielcristho/that-i-write/tree/main/terrafrom-ansible-flask)
