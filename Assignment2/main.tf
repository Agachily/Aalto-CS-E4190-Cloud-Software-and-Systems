terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {

  project = "ace-vial-326220"
  region  = "us-central1"
  zone    = "us-central1-c"
}

variable "vm_name_input" {
    type = string
    default = "css-vm-instance"
}

output "vm_name" {
  value = google_compute_instance.vm_instance.name
}

output "public_ip" {
  value = google_compute_instance.vm_instance.network_interface.0.access_config.0.nat_ip 
}

resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name_input
  machine_type = "f1-micro"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network = "default"
    access_config {
    }
  }
}
