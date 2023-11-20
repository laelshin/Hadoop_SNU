# Hadoop_SNU
Setting the Hadoop cluster at Seoul National University

Master node $\times$ 1
* CPU: Intel Xeon W-2265, 12 cores, 24 threads
* Memory: 128GB DDR4
* Disk: 1TB SSD, 24TB HDD

Worker nodes $\times$ 9
* CPU: Intel i7-13700K, 16 cores, 24 threads
* Memory: 128GB DDR5
* Disk: 500GB SSD, 64TB HDD


## Passwordless Connection
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
## Basic Setting
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
## Disk Partition 
We used 'parted', and repeated it for (a,1), (b,2), (c,3), (d,4) pairs 
```
parted /dev/sda
mklabel gpt
unit GB
mkpart primary 0 8000
print  <-- just to see the partition created
quit

mkfs.xfs /dev/sda1
mkdir /mnt/data1
mount /dev/sda1 /mnt/data1
```


## Installing Hadoop
Installing stable release of hadoop-3.3.6
```
tar -xzvf hadoop-3.3.6.tar.gz
sudo mv hadoop-3.3.6 /usr/local/hadoop
sudo wget https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
```
Setting JAVA_HOME
```
vi /usr/local/hadoop/etc/hadoop/hadoop-env.sh

export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
```

Setting .xml files at /usr/local/hadoop/etc/hadoop/

core-site.xml
```
<configuration>

<property>
    <name>hadoop.tmp.dir</name>
    <value>/mnt/data1/hdfs/tmp</value>
    <description>A base for other temporary directories.
        ~/dfs/name will be the name_node dir and
        ~/dfs/data will be the data_node dir.</description>
</property>

<property>
    <name>fs.defaultFS</name>
    <value>hdfs://sohnic:54310</value>
    <description>The name of the default file system.  A URI whose
    scheme and authority determine the FileSystem implementation.  The
    uri's scheme determines the config property (fs.SCHEME.impl) naming
    the FileSystem implementation class.  The uri's authority is used to
    determine the host, port, etc. for a filesystem.</description>
</property>

</configuration>
```
hdfs-site.xml (raid disk configuration for the name node data directory)
```
<configuration>

<property>
    <name>dfs.replication</name>
    <value>3</value>
    <description>Default block replication.
        The actual number of replications can be specified when the file is created.
        The default is used if replication is not specified in create time.
        </description>
</property>

<property>
    <name>dfs.namenode.name.dir</name>
    <value>/mnt/data1/hdfs/name</value>
</property>

<property>
    <name>dfs.datanode.data.dir</name>
    <value>/mnt/data1/hdfs/data,/mnt/data2/hdfs/data,/mnt/data3/hdfs/data,/mnt/data4/hdfs/data</value>
</property>

<property>
    <name>dfs.datanode.failed.volumes.tolerated</name>
    <value>1</value>
</property>

</configuration>
```
mapred-site.xml
```
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->

<configuration>

<property>
    <name>mapred.job.tracker</name>
    <value>sohnic:54311</value>
    <description>The host and port that the MapReduce job tracker runs
    at.  If "local", then jobs are run in-process as a single map
    and reduce task.
    </description>
</property>

<property>
    <name>mapred.framework.name</name>
    <value>yarn</value>
</property>

</configuration>
```
masters
```
sohnic
```
workers
```
node1
node2
node3
node4
node5
node6
node7
node8
node9
```




# .xml File Setting (Port Control)
# Directory Format & Run Hadoop Daemon



