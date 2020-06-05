# Failover Master Script 

## Introduction

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Distinctio aperiam pariatur omnis aliquid perspiciatis porro recusandae voluptatibus, magnam iusto, minus odit deserunt enim ipsa corrupti saepe totam at et ullam.
Lorem ipsum dolor sit amet, consectetur adipisicing elit. Distinctio aperiam pariatur omnis aliquid perspiciatis porro recusandae voluptatibus, magnam iusto, minus odit deserunt enim ipsa corrupti saepe totam at et ullam.

----
## Deploying Application

In this guide, we will deploy the Python application built using the Flask microframework on Ubuntu. We will see how to set up the Gunicorn application server and how to launch the application and configure Nginx to act as a front-end reverse proxy.

### Prerequisites

Before starting this guide, you should have:

+ A server with Ubuntu 18.04 installed and a non-root user with sudo privileges. Follow our initial server setup guide for guidance.
+ A domain name configured to point to your server. You can purchase one on Namecheap or get one for free on Freenom. You can learn how to point domains to DigitalOcean by following the relevant documentation on domains and DNS. Be sure to create the following DNS records:
	+ An A record with your_domain pointing to your server’s public IP address.
	+ An A record with www.your_domain pointing to your server’s public IP address.
+ Familiarity with the WSGI specification, which the Gunicorn server will use to communicate with your Flask application. This discussion covers WSGI in more detail.

### Step 1. Install components from Linux Repositories. 

Our first step will be to install all of the pieces we need from the Ubuntu repositories. This includes pip, the Python package manager, which will manage our Python components. We will also get the Python development files necessary to build some of the Gunicorn components.

First, let’s update the local package index and install the packages that will allow us to build our Python environment. These will include python3-pip, along with a few more packages and development tools necessary for a robust programming environment:

	$ sudo apt update

	$ sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

Similarly, we will also install Ngnix 

	$ sudo apt install nginx

Before testing Nginx, the firewall software needs to be adjusted to allow access to the service. Nginx registers itself as a service with ufw upon installation, making it straightforward to allow Nginx access.

List the application configurations that ufw knows how to work with by typing:

	$ sudo ufw app list

You should get a listing of the application profiles:
	Output
	Available applications:
	  Nginx Full
	  Nginx HTTP
	  Nginx HTTPS
	  OpenSSH

As you can see, there are three profiles available for Nginx:

+ *Nginx Full*: This profile opens both port 80 (normal, unencrypted web traffic) and port 443 (TLS/SSL encrypted traffic)
+ *Nginx HTTP*: This profile opens only port 80 (normal, unencrypted web traffic)
+ *Nginx HTTPS*: This profile opens only port 443 (TLS/SSL encrypted traffic)

It is recommended that you enable the most restrictive profile that will still allow the traffic you’ve configured. Since we haven’t configured SSL for our server yet in this guide, we will only need to allow traffic on port 80.

You can enable this by typing:

	$ sudo ufw allow 'Nginx HTTP'

You can verify the change by typing:

	$ sudo ufw status

You should see HTTP traffic allowed in the displayed output:

	Output
	Status: active

	To                         Action      From
	--                         ------      ----
	OpenSSH                    ALLOW       Anywhere                  
	Nginx HTTP                 ALLOW       Anywhere                  
	OpenSSH (v6)               ALLOW       Anywhere (v6)             
	Nginx HTTP (v6)            ALLOW       Anywhere (v6)


After this, lets move on to creating virtual Environment for our project.

### Step 2. Creating a Python Virtual Environment

Next, we’ll set up a virtual environment in order to isolate our Flask application from the other Python files on the system.

Start by installing the `python3-venv` package, which will install the `venv` module:

	$ sudo apt install python3-venv

Create a virtual environment to store your Flask project’s Python requirements by typing:

	$ python3.6 -m venv flaskenv

This will install a local copy of Python and pip into a directory called flaskenv within your project directory.

Before installing applications within the virtual environment, you need to activate it. Do so by typing:

	$ source flaskenv/bin/activate

Your prompt will change to indicate that you are now operating within the virtual environment. It will look something like this: 
`(flaskenv)user@host:~/flask_failover_master$.`

### Step 3. Clone the repository.

Download or clone this repository from github with the help of [this guide](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository). 

Once completing the cloning of the repository, enter into the repository directory and Create and activate a virtual Environment.

### Step 4. Installing packages from repository requirements

Now that you are in your virtual environment, you can install Flask and Gunicorn and get started on designing your application.

First, let’s install `wheel` with the local instance of pip to ensure that our packages will install even if they are missing wheel archives:

	$ pip install wheel

Next, let’s install all requirements from `requirements.txt`:

	$ pip install -r requirements.txt

### Step 5. Test execution of application script

After successfully installing all requirements, proceed to run the application with `flask run` command.

	$ flask run
	 * Running on http://127.0.0.1:5000/

Alternatively you can use *python -m flask:*

	$ python -m flask run
	 * Running on http://127.0.0.1:5000/

Now head over to http://127.0.0.1:5000/ to see index page.

This launches a very simple builtin server, which is good enough for testing but probably not what you want to use in production. For deployment options see Deployment Options.

### Step 6. Visibility over Network

By default Flask server is only accessible from your own computer, not from any other in the network. To make Server available over network, we will run the application with gunicorn worker.

	$ gunicorn --bind 0.0.0.0:5000 --worker-class eventlet -w 1 wsgi:app

You should see output like the following:

	Output
	[2020-06-05 12:22:34 +0530] [28217] [INFO] Starting gunicorn 20.0.4
	[2020-06-05 12:22:34 +0530] [28217] [INFO] Listening at: http://0.0.0.0:5000 (28217)
	[2020-06-05 12:22:34 +0530] [28217] [INFO] Using worker: sync
	[2020-06-05 12:22:34 +0530] [28220] [INFO] Booting worker with pid: 28220

This tells your operating system to listen on all public IPs at 5000 port.

Visit your server’s IP address with `:5000` appended to the end in your web browser again:

	http://your_server_ip:5000

When you have confirmed that it’s functioning properly, press `CTRL-C` in your terminal window.

We’re now done with our virtual environment, so we can deactivate it:

	(flaskenv) $ deactivate

Any Python commands will now use the system’s Python environment again.

### Step 7. Create systemd service file

Next, let’s create the systemd service unit file. Creating a systemd unit file will allow Ubuntu’s init system to automatically start Gunicorn and serve the Flask application whenever the server boots.

Create a unit file ending in `.service` within the `/etc/systemd/system` directory to begin:

	sudo nano /etc/systemd/system/flask_failover.service

Inside, we’ll start with the [Unit] section, which is used to specify metadata and dependencies. Let’s put a description of our service here and tell the init system to only start this after the networking target has been reached:

	[Unit]
	Description=Gunicorn instance to serve flask_failover_master
	After=network.target

Next, let’s open up the `[Service]` section. This will specify the user and group that we want the process to run under. Let’s give our regular user account ownership of the process since it owns all of the relevant files. Let’s also give group ownership to the `www-data` group so that `Nginx` can communicate easily with the Gunicorn processes. Remember to replace the username here with your username:

	[Unit]
	Description=Gunicorn instance to serve flask_failover_master
	After=network.target

	[Service]
	User=user
	Group=www-data

Next, let’s map out the working directory and set the `PATH` environmental variable so that the init system knows that the executables for the process are located within our virtual environment. Let’s also specify the command to start the service. This command will do the following:

- Start 3 worker processes (though you should adjust this as necessary)
- Create and bind to a Unix socket file, flask_failover_master.sock, within our project directory. We’ll set an umask value of 007 so that the socket file is created giving access to the owner and group, while restricting other access
- Specify the WSGI entry point file name, along with the Python callable within that file (`wsgi:app`)

Systemd requires that we give the full path to the Gunicorn executable, which is installed within our virtual environment.

Remember to replace the username and project paths with your own information:

	[Unit]
	Description=Gunicorn instance to serve flask_failover_master
	After=network.target

	[Service]
	User=user
	Group=www-data
	WorkingDirectory=/home/user/flask_failover_master
	Environment="PATH=/home/user/flask_failover_master/flaskenv/bin"
	ExecStart=/home/user/flask_failover_master/flaskenv/bin/gunicorn --workers 3 --bind unix:flask_failover_master.sock -m 007 wsgi:app

Finally, let’s add an `[Install]` section. This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running:

	[Unit]
	Description=Gunicorn instance to serve flask_failover_master
	After=network.target

	[Service]
	User=user
	Group=www-data
	WorkingDirectory=/home/user/flask_failover_master
	Environment="PATH=/home/user/flask_failover_master/flaskenv/bin"
	ExecStart=/home/user/flask_failover_master/flaskenv/bin/gunicorn --bind unix:flask_failover_master.sock -m 007 wsgi:app

	[Install]
	WantedBy=multi-user.target


With that, our systemd service file is complete. Save and close it now.

We can now start the Gunicorn service we created and enable it so that it starts at boot:

	sudo systemctl start flask_failover_master
	sudo systemctl enable flask_failover_master

Let’s check the status:

	sudo systemctl status flask_failover_master

You should see output like this:

	Output
	● flask_failover_master.service - Gunicorn instance to serve flask_failover_master
	   Loaded: loaded (/etc/systemd/system/flask_failover_master.service; enabled; vendor preset: enabled)
	   Active: active (running) since Fri 2018-07-13 14:28:39 UTC; 46s ago
	 Main PID: 28232 (gunicorn)
		Tasks: 4 (limit: 1153)
	   CGroup: /system.slice/flask_failover_master.service
			├─28232 /home/user/flask_failover_master/flaskenv/bin/python3.6 /home/user/flask_failover_master/flaskenv/bin/gunicorn --workers 3 --bind unix:flask_failover_master.sock -m 007
			├─28250 /home/user/flask_failover_master/flaskenv/bin/python3.6 /home/user/flask_failover_master/flaskenv/bin/gunicorn --workers 3 --bind unix:flask_failover_master.sock -m 007
			├─28251 /home/user/flask_failover_master/flaskenv/bin/python3.6 /home/user/flask_failover_master/flaskenv/bin/gunicorn --workers 3 --bind unix:flask_failover_master.sock -m 007
			└─28252 /home/user/flask_failover_master/flaskenv/bin/python3.6 /home/user/flask_failover_master/flaskenv/bin/gunicorn --workers 3 --bind unix:flask_failover_master.sock -m 007
If you see any errors, be sure to resolve them before continuing with the tutorial.

### Step 8. Configuring Nginx to Proxy Requests

Our Gunicorn application server should now be up and running, waiting for requests on the socket file in the project directory. Let’s now configure Nginx to pass web requests to that socket by making some small additions to its configuration file.

Begin by creating a new server block configuration file in Nginx’s sites-available directory. Let’s call this flask_failover_master to keep in line with the rest of the guide:

	sudo nano /etc/nginx/sites-available/flask_failover_master

Open up a server block and tell Nginx to listen on the default port 80. Let’s also tell it to use this block for requests for our server’s domain name:

	server {
		listen 80;
		server_name your_domain www.your_domain;
	}

Next, let’s add a location block that matches every request. Within this block, we’ll include the proxy_params file that specifies some general proxying parameters that need to be set. We’ll then pass the requests to the socket we defined using the proxy_pass directive:

	server {
		listen 80;
		server_name your_domain www.your_domain;

		location / {
			include proxy_params;
			proxy_pass http://unix:/home/user/flask_failover_master/flask_failover_master.sock;
		}
	}
Save and close the file when you’re finished.

To enable the Nginx server block configuration you’ve just created, link the file to the sites-enabled directory:

	sudo ln -s /etc/nginx/sites-available/flask_failover_master /etc/nginx/sites-enabled

With the file in that directory, you can test for syntax errors:

	sudo nginx -t

If this returns without indicating any issues, restart the Nginx process to read the new configuration:

	sudo systemctl restart nginx

Finally, let’s adjust the firewall. We can then allow full access to the Nginx server:

	sudo ufw allow 'Nginx Full'

You should now be able to navigate to your server’s IP or domain name in your web browser:

	http://IP_address

OR

	http://your_domain

----

## Logging functionality:

Logging is a means of tracking events that happen when some software runs. The logging calls are added to the code to indicate that certain events have occurred. An event is described by a descriptive message which can optionally contain variable data (i.e. data that is potentially different for each occurrence of the event). Events also have an importance which the developer ascribes to the event; the importance can also be called the level or severity.

This program generates 2 distinct logs.
1. First for keep alive log generate by periodic ping (ping.log) and
1. second for maintaining logs generated by communication events with the master node.

### Levels of Logs

	1. DEBUG	Detailed information, typically of interest only when diagnosing problems.
	2. INFO		Confirmation that things are working as expected.
	3. WARNING	An indication that something unexpected happened, or indicative of some problem in the near future. The software is still working as expected.
	4. ERROR	Due to a more serious problem, the software has not been able to perform some function.
	5. CRITICAL	A serious error, indicating that the program itself may be unable to continue running.

### Format followed by the loggers is:

	'[TIMESTAMP] [LOGGERNAME] [LOG LEVEL] - [Message]'
