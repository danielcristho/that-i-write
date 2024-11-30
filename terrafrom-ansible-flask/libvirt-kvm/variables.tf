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