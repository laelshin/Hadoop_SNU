# Hadoop_SNU
The Hadoop setting procedure at SNU
1 Master node, 9 Worker nodes

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
```
sudo apt update
sudo apt install vim
sudo apt install git
sudo apt install tmux
```

# Disk Partition
# .xml File Setting (Port Control)
# Directory Format & Run Hadoop Daemon



