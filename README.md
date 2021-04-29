# CS643-Cloud-computing

Cloud computing cs643 – Project 2
JT289  Jinhong Tan
April 2021


Section1: AWS EMR, 4 instances run spark script
Section2: EC2 Instance without Docker					
Section3: EC2 Instance Docker					


AWS EMR, 4 instances run spark script

With Amazon EMR, users can set up a cluster to process and analyze data with big data frameworks. EMR can launch a sample cluster using Spark, and run a simple PySpark script that store in an Amazon S3 bucket. Total 4 instance will create and one is the master instance, other three are workers.

1.	Prepare storage for cluster input and output
    (1)Create an Amazon S3 bucket
    Upload the PySpark script, trainingdataset.cvs validationdataset.cvs

2.	Launch an Amazon EMR cluster
1)	Sign into the AWS Management Console and open the Amazon EMR console.
2)	Choose Create cluster to open the Quick Options wizard.
3)	Enter a Cluster name, Under Applications, choose the Spark option.
4)	Under Security and access choose the EC2 key pair which were created before or create a new one.
5)	Click Create cluster to launch the cluster. The cluster should in Waiting status.

3.	Submit work to Amazon EMR
1)	Click the Cluster you created, make sure it is in a Waiting state
2)	Choose Steps, and them choose Add step.
3)	For Step type, choose Spark application.
4)	For Application location, enter the location of python script in Amazon S3.
5)	In the Arguments field. Enter the following arguments and values:
--data_source s3://jt289project2/trainingdataset.csv
--output_uri s3://jt289project2/myOutputFolder

6)	Choose Add to submit the step. The python script starting to run and will be done after completed.

4.	Open S3 console, choose bucket jt289p roject2, choose myoutputfolder. A result file should be stored under this path.


EC2 Instance without Docker					
1.	Creating EC2 Instance
1)	Under Compute Column in the AWS Management Console Click EC2
2)	Under the Instances click Create Instance
3)	Select the AMI of your choice. Amazon Linux 2 AMI is usually preferred
4)	StSelect Instance Type I've chosen t2.micro as I'm using AWS Educate and this gives me t2.micro under free tier elgible
5)	Step 5: Here one can either review and launch or tweak security, configuration and storage features of EC2.
6)	Launch EC2 Instance
2.	SSH EC2 instance
1)	Open terminal, go to the path where pem key pair file saved
Chmod 400 project2key.pem
ssh -i "project2key.pem" root@ec2-54-242-207-60.compute-1.amazonaws.com
2)	You should have connected to the instance

3.	Installing Spark on EC2 Instance
1)	Update EC2 in terminal
Sudo yum update -y
2)	Check python version 
python3 –version
3)	Instal pip
Sudo pip install –upgrade pip
4)	Install Java
Sudo apt-get install default-jre
Java --version
5)	Install Py4j used for communicate between java and python
Pip install py4j
6)	Install Spark and Hadoop
wget http://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop2.7.tgz
sudo tar -zxvf spark-3.0.0-bin-hadoop2.7.tgz
7)	Install findspark
Sudo pip install findspark

4.	Running your Application in EC2
1)	Upload predict.py file to the Ec2 instance 
scp -i <"your .pem file"> predict.py :~/predict.py

2)	Run the following command in Ec2 instance to start the model prediction (data from s3 which set to public): 
spark-submit --packages org.apache.hadoop:hadoop-aws:2.7.4 predict.py s3://jt289project2/ValidationDataset.csv


EC2 Instance with Docker
Following the procedures from above to create instance to set up the environment. (step 1 to step7).

1.	Installation 
1)	Install the Docker package
sudo yum install docker -y
2)	Run the Docker service
sudo service docker start
3)	Add EC2 user to the docker group
sudo usermod -a -G docker ec2-user
4)	Verify the EC2-user can run Docker commands
docker  --version or docker info

2.	Create a Dockerfile

touch Dockerfile
3.	nano Dockerfile and create the Dockerfile Image to automate the process
sudo docker build . -f Dockerfile -t <Image name of your choice>
Pushing and Pulling created Image to DockerHub
4.	Login to your dockerhub account through ec2
docker login: Type your credentials
5.	In order to push docker type the following commands
docker tag <Local Ec2 Repository name>:<Tag name> <dockerhub username>/<local Ec2 Repository name>
docker push <dockerhub username>/<local Ec2 Repository name>

3.	Pulling your Dockerimage back to Ec2
docker pull <dockerhub username>/<Repository name>:<tag name>
Example:
docker pull sampathgonnuru/cs643-project2:latest
4.	Running my dockerimage
sudo docker run -t <Given Image name>

docker run -it sampathgonnuru/cs643-project2:latest s3//mywineproject/ValidationDataset.csv 

