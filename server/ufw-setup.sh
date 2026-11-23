#!/bin/bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'Allow SSH remote admin'
sudo ufw allow 80/tcp comment 'Allow HTTP web traffic'
sudo ufw --force enable
sudo ufw status verbose
