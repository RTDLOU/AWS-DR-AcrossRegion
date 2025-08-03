#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install Flask boto3

mkdir -p /home/ec2-user/myapp
cp app.py /home/ec2-user/myapp/

chown -R ec2-user:ec2-user /home/ec2-user/myapp

systemctl stop httpd
systemctl disable httpd

cd /home/ec2-user/myapp
nohup python3 app.py > flask.log 2>&1 &
