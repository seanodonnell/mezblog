#!/bin/sh
#Assign existing hostname to $hostn
hostn=$(cat /etc/hostname)
newhost="$1"

#change hostname in /etc/hosts & /etc/hostname
#sudo sed -i "s/$hostn/$newhost/g" /etc/hosts
sudo sed -i "s/$hostn/$newhost/g" /etc/hostname

sudo sed -i "1i 127.0.0.1 $newhost" /etc/hosts

sudo hostname $newhost
sudo DEBIAN_FRONTEND=noninteractive apt-get -y update
sudo DEBIAN_FRONTEND=noninteractive Dpkg::Options::="--force-confdef" Dpkg::Options::="--force-confold" apt-get -y upgrade
sudo DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:saltstack/salt
sudo DEBIAN_FRONTEND=noninteractive apt-get -y update
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install salt-minion
sudo service salt-minion stop
sudo sed -i '1i master: 172.16.0.155' /etc/salt/minion
