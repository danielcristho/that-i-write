provider "libvirt" {
  uri = "qemu:///system"
}

resource "null_resource" "cache_image" {
  provisioner "local-exec" {
    command = "wget -O /tmp/ubuntu-20.04.qcow2 ${var.ubuntu_20_img_url}"
  }
}

# Volume untuk base image
resource "libvirt_volume" "base" {
  name   = "base.qcow2"
  source = "/tmp/ubuntu-20.04.qcow2"
  pool   = var.libvirt_disk_path
  format = "qcow2"
  depends_on = [null_resource.cache_image]
}

# Volume untuk VM dengan ukuran 10GB
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