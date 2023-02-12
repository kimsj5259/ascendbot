terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.54.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region     = var.region
  # Hard-coding credentials is not recommended
  access_key = var.access_key
  secret_key = var.secret_key
}

resource "tls_private_key" "ascend" {
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "aws_instance" "example" {
  ami           = "ami-0454bb2fefc7de534"
  instance_type = "t2.micro"

  tags = {
    Name = "bot-example"
  }

  connection {
    host     = self.public_ip
    type     = "ssh"
    user     = "ec2-user"
    private_key = tls_private_key.ascend
  }

  provisioner "file" {
    source      = "ascendbot/tradingbot.py"
    destination = "/home/ec2-user/tradingbot.py"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/ec2-user/script.py",
      "nohup /home/ec2-user/script.py > /dev/null 2>&1 &",
    ]
  }
}