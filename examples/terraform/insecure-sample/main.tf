# Deliberately insecure demo fixture for the IaC reviewer.
# Do not apply. This exists only to exercise static Well-Architected checks.

resource "aws_s3_bucket" "public_assets" {
  bucket = "iac-reviewer-public-assets-demo"
  acl    = "public-read"
}

resource "aws_security_group" "admin" {
  name        = "iac-reviewer-admin"
  description = "Permissive admin access for negative test coverage"

  ingress {
    description = "SSH from anywhere - intentionally risky"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "orders" {
  identifier        = "iac-reviewer-orders"
  allocated_storage = 20
  engine            = "postgres"
  instance_class    = "db.t4g.micro"
  username          = "demo"
  password          = "replace-me"
}

resource "aws_instance" "oversized" {
  ami           = "ami-1234567890abcdef0"
  instance_type = "m5.24xlarge"
}
