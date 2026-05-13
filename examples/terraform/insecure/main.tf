terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "Demo AWS region; static scanner fixture only, do not apply."
  type        = string
  default     = "ap-northeast-1"
}

resource "aws_s3_bucket" "public_artifacts" {
  bucket = "iac-reviewer-public-artifacts-demo"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "public_artifacts" {
  bucket                  = aws_s3_bucket.public_artifacts.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_security_group" "admin" {
  name        = "iac-reviewer-public-admin"
  description = "Intentionally insecure fixture: SSH open to the internet."

  ingress {
    description = "Public SSH for scanner detection"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "orders" {
  identifier          = "iac-reviewer-orders-demo"
  allocated_storage   = 20
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  username            = "demo"
  password            = "not-for-apply-demo-only"
  skip_final_snapshot = true
}

resource "aws_instance" "oversized" {
  ami           = "ami-1234567890abcdef0"
  instance_type = "m5.24xlarge"
}
