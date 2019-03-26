# Current weather and currency converter REST Application

This Flask application enables you to get the weather of a certain city and it also has a currency converter.

The application uses two REST API's, available publicly for free but requires registration.

You can type a city/town, and the result will give you a summary of the current weather i.e "Clear Sky" and the temperature.

You can also check the current currency exchange rate for any two given world currencies.


## Setup


The assumption is you have a Cassandra cluster setup already, with a keyspace called "weatherhistory" and a table called "weatherhistory" loaded from the csv file provided "weatherHistory.csv". Steps to create and load this file is provided in the appendix below.


1. External API Registration

Weather - https://openweathermap.org/api 
select "Current weather data" option and register to optain API key

Currency - https://openexchangerates.org
select "Free Plan" option and sign-up to optain API key



Initial setup
2. Create a folder called "instance"
   - Within instance folder, create a file called "config.py"
    - Edit the file and add the following - replacing the API key from above step after registering.
```
DEBUG = False
API_KEY_WEATHER = "Weather API Key"
API_KEY_CURRENCY = "Currency API Key"
```
3. Create a file called "config.py" in the root folder.
  3.1 Edit the file and add 
```
DEBUG = False
```
  3.2 during development, you can change DEBUG to "True"

## RESTfull app
The application provides historical weather data (stored in a Cassandra database) via a REST API.
http://[HOSTNAME]/weather/[city]/[date]

example 
http://0.0.0.0:8080/weather/london/20060401








## Deploying on GCP

#########################################################
###### 1. Preparing for cluster deployment (on gcloud)
#########################################################

```
gcloud config set project intrepid-abacus-229322
gcloud config set compute/zone europe-west2-b
```

export your project ID to an environment variable, called PROJECT_ID:
```
export PROJECT_ID="$(gcloud config get-value project -q)"
```

build our docker image:
```
docker build -t gcr.io/${PROJECT_ID}/my_first_app_image:v1 .
```

If you need to to delete
```
docker rmi gcr.io/${PROJECT_ID}/my_first_app_image:v1 --force
```

push our image to the gcr private repository of google cloud:
```
gcloud auth configure-docker
```
y to confirm
```
docker push gcr.io/${PROJECT_ID}/my_first_app_image:v1
```

run container “locally” (on the google shell computer) to make sure all is fine:
```
docker run --rm -p 8080:8080 gcr.io/${PROJECT_ID}/my_first_app_image:v1

docker run --rm -p 8080:8080 gcr.io/intrepid-abacus-229322/my_first_app_image:v1
```
#######################################################
###### 2. Preparing a container cluster    ############
#######################################################

creates a 3 node cluster named cassandra:
gcloud container clusters create cassandra --num-nodes=3

see the nodes that are created (each a separate VM)
gcloud compute instances list

#######################################################
###### 3. Deploying our application          ####
######################################################

```
kubectl run cassandra --image=gcr.io/${PROJECT_ID}/my_first_app_image:v1 --port 8080
```
To delete deployment
```
kubectl delete deployment cassandra
```
see the pods created:
```
kubectl get pods
```

To expose our cluster to the external world (internet!), we need to create a “service” resource, which provides
networking and IP support to our application’s pods: (all in one line):
```
kubectl expose deployment cassandra --type=LoadBalancer --port 80 --target-port 8080
```
To delete service
```
kubectl delete service cassandra
```
get the external IP address that is assigned to our deployment by running:

```
kubectl get service
```

check url: my ip address was;
http://35.246.104.30/

http://35.246.104.30/weather/london/20060401



To see a brief status of our deployment:
```
kubectl get deployment cassandra
```
#Specially, pay attention under column AVAILABLE.
#For a more detailed status report, issue:
kubectl describe deployment cassandra

#If all is fine, it could be that the firewall ruleset does not allow external HTTP requests to our 
#load-balancer. Check the firewall ruleset by issuing:
gcloud compute firewall-rules list
#Look for a line that allows INGRESS for "DIRECTION" and for "ALLOW" it should be tcp:80 and for "DISABLED" should # be False.




###########################################################
###### 4.Scaling up our application   #####################
###########################################################
```
kubectl scale deployment cassandra --replicas=2
```

You can check the number of replicas by issuing:
```
kubectl get deployment cassandra

kubectl get pods

kubectl get service cassandra

```
