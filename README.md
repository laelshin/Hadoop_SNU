# Hadoop_SNU
Setting the Hadoop cluster at Seoul National University

1 Master node
* CPU: Intel Xeon W-2265, 12 cores, 24 threads
* Memory: 128GB DDR4
* Disk: 1TB SSD, 24TB HDD

9 Worker nodes
* CPU: Intel i7-13700K, 16 cores, 24 threads
* Memory: 128GB DDR5
* Disk: 500GB SSD, 64TB HDD


# Passwordless Connection
```
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat id_rsa.pub >> authorized_keys
chmod 0600 ./authorized_keys 
```
```
lshin@sohnic:~$ cat .ssh/config

Host *
	IdentityFile ~/.ssh/id_rsa
   	StrictHostKeyChecking=no
```
# Basic Setting
We need to download relevant packages at the every node.
```
sudo apt update
sudo apt install vim
sudo apt install git
sudo apt install tmux
```
Downloading JAVA
```
sudo apt install openjdk-11-jdk openjdk-11-jre
```
```
root@sohnic:/etc# java -version

openjdk version "11.0.20" 2023-07-18
OpenJDK Runtime Environment (build 11.0.20+8-post-Ubuntu-1ubuntu122.04)
OpenJDK 64-Bit Server VM (build 11.0.20+8-post-Ubuntu-1ubuntu122.04, mixed mode, sharing)
```
Checking hosts file
```
root@sohnic:/etc# cat /etc/hosts

127.0.0.1 localhost

# The following lines are desirable for IPv6 capable hosts
::1   ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

# Data nodes
192.168.0.130 sohnic
192.168.0.131 node1
192.168.0.132 node2
192.168.0.133 node3
192.168.0.134 node4
192.168.0.135 node5
192.168.0.136 node6
192.168.0.137 node7
192.168.0.138 node8
192.168.0.139 node9
```
Checking Ubuntu version
```
root@sohnic:/etc# lsb_release -a

No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 22.04.1 LTS
Release:	22.04
Codename:	jammy
```
# Disk Partition
# .xml File Setting (Port Control)
# Directory Format & Run Hadoop Daemon



