# Failover Worker Script 

## Introduction

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Distinctio aperiam pariatur omnis aliquid perspiciatis porro recusandae voluptatibus, magnam iusto, minus odit deserunt enim ipsa corrupti saepe totam at et ullam.

----
##Implementation

### Install python

- For Windows:
1. Download Installer from [here](https://www.python.org/downloads/windows/) and Install python 3 (preferably version 3.7 or higher)
2. Follow [this guide](https://www.howtogeek.com/197947/how-to-install-python-on-windows/) in case of any issues. 
3. Check if installation is successful by running given command in command prompt.
	'python3 –version'
4. If installed properly, The output should read installed version of python.
5. **Note:** Run the command prompt as administer for executing this program.

- For Linux:
1. Refer to [this guide](https://docs.python-guide.org/starting/install3/linux/) to install and verify python installation.

### Install pip (package installer for python)

pip is the reference Python package manager. It’s used to install and update packages. You’ll need to make sure you have the latest version of pip installed.

- For Windows:
1. Windows Installer for Python include pip by default. To verify the version, use 

	'py -m pip --version'

2. You can make sure that pip is up-to-date by running:

	'py -m pip install --upgrade pip' 

### Install virtualenv using pip

[virtualenv](https://packaging.python.org/key_projects/#virtualenv) is used to manage Python packages for different projects. Using virtualenv allows you to avoid installing Python packages globally which could break system tools or other projects. You can install virtualenv using pip.

On Windows:

'py -m pip install --user virtualenv'

On macOS and Linux:

'python3 -m pip install --user virtualenv'

### Clone the repository:

Download the repository from github with the help of [this guide](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository). Once completing the cloning of the repository, enter into the failover_worker directory and Create and activate a virtual Environment.

### Creating Virtual Environment

venv (For python2) and virtualenv (for python2) allow you to manage separate package installations for different projects. They essentially allow you to create a “virtual” isolated Python installation and install packages into that virtual installation.

To create a virtual environment, go to your project’s directory and run venv. If you are using Python 2, replace venv with virtualenv in the below commands.

On macOS and Linux:

'python3 -m venv env'

or

'python -m virtualenv env'

On Windows:

'py -m venv env'

The second argument is the location to create the virtual environment. Generally, you can just create this in your project and call it env.

venv will create a virtual Python installation in the env folder.

### Activating Virtual Environment

Before you can start installing or using packages in your virtual environment you’ll need to activate it. Activating a virtual environment will put the virtual environment-specific python and pip executables into your shell’s PATH.

After entering  

On macOS and Linux:

'source env/bin/activate'

On Windows:

'.\env\Scripts\activate'

### Leaving Virtual Environment

To leave virtual environment, simply run:
'deactivate'

### Installing packages

Once you activate virtual environment, you can proceed to install packages. For example, to install requests library, run:

'pip install requests'

or for specific version:

'pip install requests==2.18.4'

As we already have all requirements specified in the requirements.txt file, we will skip this part and install requirements from 'requirements.txt'

### Using requirements files:

To install requrirements from requirements file, run:

'pip install -r requirements.txt'

### Execute Application script:

After successfully installing all requirements, proceed to run the application.
To do this, you can either use the flask command or python’s -m switch with Flask. Before you can do that you need to tell your terminal the application to work with by exporting the FLASK_APP environment variable:

	$ export FLASK_APP=hello.py
	$ flask run
	 * Running on http://127.0.0.1:5000/

If you are on Windows, the environment variable syntax depends on command line interpreter. On Command Prompt:

	C:\path\to\app>set FLASK_APP=hello.py

And on PowerShell:

	PS C:\path\to\app> $env:FLASK_APP = "hello.py"

Alternatively you can use *python -m flask:*

	$ export FLASK_APP=hello.py
	$ python -m flask run
	 * Running on http://127.0.0.1:5000/

This launches a very simple builtin server, which is good enough for testing but probably not what you want to use in production. For deployment options see Deployment Options.

Now head over to http://127.0.0.1:5000/ to see index page.

### Visibility over Network

By default Flask server is only accessible from your own computer, not from any other in the network. To make Server available over network, simply add *'--host=0.0.0.0'* to the command line.

	$ flask run --host=0.0.0.0

This tells your operating system to listen on all public IPs.

NOTE: This type of execution is to be performed on the development process and you need to follow deployment guide below to deploy Flask application on your system.

----

## Deployment steps:

To be added.

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
