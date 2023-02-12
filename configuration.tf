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
    private_key = file("~/.ssh/id_rsa")
  }

  provisioner "file" {
    source      = "jin/ascend/tradingbot.py"
    destination = "/home/ec2-user/tradingbot.py"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/ec2-user/script.py",
      "nohup /home/ec2-user/script.py > /dev/null 2>&1 &",
    ]
  }
}

# resource "aws_security_group" "instance" {
# 	name = "terraform-example"

# 	ingress {
# 		from_port = 8080
# 		to_port = 8080
# 		protocol = "tcp"
# 		cidr_blocks = ["0.0.0.0/0"]
# 	}

# }