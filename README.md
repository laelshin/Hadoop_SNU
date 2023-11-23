# Hadoop_SNU
Setting the Hadoop cluster at Seoul National University (Advisor: Sungryong Hong (KASI), Jubee Sohn (SNU))

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
Setting HADOOP_HOME
```
vi .bashrc

# Hadoop bin
export HADOOP_HOME=/usr/local/hadoop
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
```
Formatting the name node
```
sudo rm -rf /mnt/data1/hdfs
sudo mkdir -pv /mnt/data1/hdfs/name
sudo chown -R lshin /mnt/data1/hdfs
sudo chown -R lshin /usr/local/hadoop
hdfs namenode -format
```
##Starting and Stopping Hadoop
We should run *start-dfs.sh* to start the hdfs-daemon, and run *stop-dfs.sh* to stop the daemon.
```
alias hadoopon='/usr/local/hadoop/sbin/start-dfs.sh`
alias hadoopoff='/usr/local/hadoop/sbin/stop-dfs.sh`
alias hfs='hadoop fs'
```
Monitoring Hadoop at the name node
```
lshin@sohnic:~$ jps

711017 NameNode
711341 SecondaryNameNode
711509 Jps
```
at the worker node
```
lshin@node1:~$ jps

436803 Jps
436590 DataNode
```

## Hadoop webUI 
Setting an exporting alias at the personal laptop
```
alias xporthadoop='ssh -N -L 9870:localhost:9870 lshin@sohnic.snu.ac.kr
```
Accessing the local browser with an address *localhost:9870*
![alt text](https://github.com/laelshin/Hadoop_SNU/blob/main/Hadoop_webUI.png)

## Downloading Scala
Downloading Scala in every node.
```
sudo wget www.scala-lang.org/files/archive/scala-2.13.0.deb
sudo dpkg -i scala-2.13.0.deb
scala
```

## Downloading Spark
```
sudo wget https://archive.apache.org/dist/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3-scala2.13.tgz
tar -xzvf spark-3.4.1-bin-hadoop3-scala2.13.tgz
sudo mv spark-3.4.1-bin-hadoop3-scala2.13.tgz /usr/local/spark
sudo chown -R lshin /usr/local/spark
```
## Downloading Python
Downloading python3, jupyter notebook, jupyter lab, and python packages in every node.
```
apt install python3-pip
pip install numpy scipy scikit-learn pyarrow tqdm astropy pandas
pip install jupyterlab
pip install notebook
pip install pyspark==3.4.1
pip list |grep spark
pyspark                   3.4.1
```

## Setting Spark
```
vi /usr/local/saprk/conf/workers

node1
node2
node3
node4
node5
node6
node7
node8
node9

vi .bashrc

# Java Home
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export PATH=$JAVA_HOME:$PATH

# Hadoop path
export HADOOP_HOME=/usr/local/hadoop
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH

# Scala Home
export SCALA_HOME=/usr/share/scala
export PATH=$SCALA_HOME/bin:$PATH

# Spark Home
export SPARK_HOME=/usr/local/spark
export PYTHONPATH=/usr/local/spark/python/:$PYTHONPATH
export PYTHONPATH=/usr/local/spark/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH
export PATH=$SPARK_HOME/bin:$PATH

# PySpark paths
export PYSPARK_PYTHON=/usr/bin/python3


# some minor bug-busting settings and misc.
export TERM=xterm-color
export PATH=/home/shong/mybin:$PATH

alias sparkon='$SPARK_HOME/sbin/start-master.sh -h sohnic && $SPARK_HOME/sbin/start-workers.sh spark://sohnic00:7077'
alias sparkoff='$SPARK_HOME/sbin/stop-all.sh'
```
Running a spark stand-alone example
```
spark-submit --master spark://sohnic:7077 /usr/local/lib/python3.10/dist-packages/pyspark/examples/src/main/python/pi.py 100

Pi is roughly 3.144280
```

## Spark webUI 
Setting an exporting alias at the personal laptop
```
alias xportspark='ssh -N -L 8080:localhost:8080 lshin@sohnic.snu.ac.kr'
```
Accessing the local browser with an address *localhost:8080*
![alt text](https://github.com/laelshin/Hadoop_SNU/blob/main/Spark_webUI.png)

## Setting Jupyter notebook
Running Jupyter notebook with --no-browser option
```
vi .bashrc

alias jupon='jupyter notebook --no-browser --port=7788'
alias labon='jupyter lab --no-browser --port=8899'

jupyter notebook password
```
Connecting with a labtop
```
alias xportjup='ssh -N -L 7788:localhost:7788 lshin@sohnic.snu.ac.kr'
```

Running another spark stand-alone example with jupyter notebook

[https://github.com/shongscience/misc/tree/master/pyspark-tutorial](https://github.com/shongscience/misc/tree/master/pyspark-tutorial)

Making Spark session
```
from pyspark.sql import SparkSession

# Initialize a SparkSession
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("spark://sohnic:7077") \
    .config("spark.driver.memory", "16g") \
    .config("spark.executor.memory", "58g") \
    .config("spark.jars.packages", "graphframes:graphframes:0.7.0-spark2.4-s_2.11") \
    .getOrCreate()
```

# Setting YARN
```
vi .bashrc

export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
alias yarnon='/usr/local/hadoop/sbin/start-yarn.sh'
alias yarnoff='/usr/local/hadoop/sbin/stop-yarn.sh'
```

Setting the xml files
```
vi /usr/local/hadoop/etc/hadoop/yarn-site.xml

<?xml version="1.0"?>
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
<configuration>

<property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>sohnic:8025</value>
</property>
<property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>sohnic:8035</value>
</property>
<property>
    <name>yarn.resourcemanager.address</name>
    <value>sohnic:8050</value>
</property>

<!-- Site specific YARN configuration properties -->

<!-- Global cluster settings -->
<property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>120000</value>
    <description>Amount of physical memory to be made available for containers on each node.</description>
</property>
<property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>20</value>
    <description>Number of CPU cores to be made available for containers on each node.</description>
</property>

<!-- Application-specific settings -->
<property>
    <name>yarn.scheduler.minimum-allocation-mb</name>
    <value>1024</value>
    <description>Minimum memory allocation for a container.</description>
</property>
<property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>120000</value>
    <description>Maximum memory allocation for a container.</description>
</property>
<property>
    <name>yarn.scheduler.minimum-allocation-vcores</name>
    <value>1</value>
    <description>Minimum number of virtual CPU cores that can be allocated for a container.</description>
</property>
<property>
    <name>yarn.scheduler.maximum-allocation-vcores</name>
    <value>20</value>
    <description>Maximum number of virtual CPU cores that can be allocated for a container.</description>
</property>

<!-- Permission settings -->
<property>
  <name>yarn.resourcemanager.principal</name>
  <value>lshin</value>
</property>

<property>
  <name>yarn.nodemanager.principal</name>
  <value>lshin</value>
</property>

</configuration>
```

## YARN webUI 
Setting an exporting alias at the personal laptop
```
alias xportyarn='ssh -N -L 8088:localhost:8088 lshin@sohnic.snu.ac.kr'
```
Accessing the local browser with an address *localhost:8080*
![alt text](https://github.com/laelshin/Hadoop_SNU/blob/main/Spark_webUI.png)

Making Spark session with YARN and running the Jupyter notebook example again
```
# PySpark packages
from pyspark import SparkContext   
#from pyspark.sql import SQLContext; SQLContex is obsolete !! using SparkSession
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("yarn") \
    .appName("spark-shell") \
    .config("spark.driver.maxResultSize", "32g") \
    .config("spark.driver.memory", "64g") \
    .config("spark.executor.memory", "7g") \
    .config("spark.executor.cores", "1") \
    .config("spark.executor.instances", "50") \
    .getOrCreate()

sc = spark.sparkContext
sc.setCheckpointDir("hdfs://sohnic:54310/tmp/spark/checkpoints")

import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark import Row
from pyspark.sql.window import Window as W
```
