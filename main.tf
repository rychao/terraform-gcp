provider "google" {
  version = "~> 2.0"
  project = var.project
  region  = var.region
}

resource "google_compute_network" "pliny" {
  name                    = "${var.prefix}-vpc-${var.region}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "pliny" {
  name          = "${var.prefix}-subnet"
  region        = var.region
  network       = google_compute_network.pliny.self_link
  ip_cidr_range = var.subnet_prefix
}

resource "google_compute_firewall" "http-server" {
  name    = "default-allow-ssh-http"
  network = google_compute_network.pliny.self_link

  allow {
    protocol = "tcp"
    ports    = ["22", "80"]
  }

  // Allow traffic from everywhere to instances with an http-server tag
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

resource "tls_private_key" "ssh-key" {
  algorithm = "RSA"
  rsa_bits  = "4096"
}

resource "null_resource" "gcpkey" {
  provisioner "local-exec" {
    command = "echo \"${tls_private_key.ssh-key.private_key_pem}\" > gcpkey.pem"
  }

  provisioner "local-exec" {
    command = "chmod 600 gcpkey.pem"
  }
}

resource "google_compute_instance" "pliny" {
  count        = var.instance_count
  name         = "${var.prefix}-instance-${count.index}"
  zone         = "${var.region}-${var.zone}"
  machine_type = var.machine_type

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-1804-lts"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.pliny.self_link
    access_config {
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${chomp(tls_private_key.ssh-key.public_key_openssh)} terraform"
  }

  tags = ["http-server"]

  labels = {
    name = "pliny"
  }

}

resource "null_resource" "configure-pliny-app" {
  count      = var.instance_count
  depends_on = [
    google_compute_instance.pliny,
  ]

  triggers = {
    build_number = timestamp()
  }

  provisioner "file" {
    source      = "files/"
    destination = "/home/ubuntu/"

    connection {
      type        = "ssh"
      user        = "ubuntu"
      timeout     = "300s"
      private_key = tls_private_key.ssh-key.private_key_pem
      host        = element(google_compute_instance.pliny.*.network_interface.0.access_config.0.nat_ip, count.index)
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x *.sh",
      "chmod +x *.py",
      "./deploy_app.sh"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      timeout     = "300s"
      private_key = tls_private_key.ssh-key.private_key_pem
      host        = element(google_compute_instance.pliny.*.network_interface.0.access_config.0.nat_ip, count.index)
    }
  }
}
