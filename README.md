# spwebapp: A sample online furniture shop with a flask based backend and HTML frontend
[![Linters](https://github.com/amiket23/spwebapp/actions/workflows/linters.yml/badge.svg)](https://github.com/amiket23/spwebapp/actions/workflows/linters.yml)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Famiket23%2Fspwebapp.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Famiket23%2Fspwebapp?ref=badge_shield)
[![CodeQL](https://github.com/amiket23/spwebapp/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/amiket23/spwebapp/actions/workflows/github-code-scanning/codeql)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

The main branch has secure code while the develop branch has vulnerable code. This project is a part of an academic exercise.

## Use Case

![MicrosoftTeams-image (1)](https://user-images.githubusercontent.com/65346396/235259148-fecce913-d77f-4372-91c0-b263f42eab6e.png)

## Prerequisites

The package has been tested with the following prerequisites:

+ Python 3.9
+ Microsoft SQL Server 2022
+ Microsoft SQL Server Management Studio 19.0.2
+ Flask 2.3.1
+ Flask-Bcrypt 1.0.1
+ Flask-Login 0.6.2
+ Flask-SQLAlchemy 3.0.3

## Quickstart: Setting up Python
### Instructions for Windows:
* Go to the [page](https://www.python.org/downloads/windows/) and find the latest stable release of Python
* On this page move to Files and download Windows x86-64 executable installer for 64-bit or Windows x86 executable installer for 32-bit
* Run the python installer
* Make sure to mark Add Python 3.x to PATH otherwise you will have to do it explicitly afterwards
* After installation is complete click on Close. You can launch python from start now to check that it is working.
### Instructions for Linux:
* On most Linux systems including the following OS - Ubuntu, Linux Mint, Debian, openSUSE, CentOS, Fedora, Arch Linux, Python is already installed
* You can check it using the following command from the terminal:
```bash
$ python --version
```
* You can upgrade to the required version by running the following command:
```bash
$ sudo apt-get install python3.x
```
* To verify the installation enter the following commands in your Terminal:
```bash
python3.x
```
### Instructions for MAC:
* Download and install Homebrew Package Manager if it isn't already installed
 * Open Terminal from Application -> Utilities. Enter following command in macOS terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
* Enter the system password if prompted. After you see a message called “Installation Successful”. You are ready to install python version 3 on your macOS.
* Open Terminal from Application -> Utilities and enter following command:
```bash
brew install python3
```
* After command processing is complete,  enter following command in your Terminal app to verify:
```bash
python
```
## Quickstart:

### Instructions:
1. Clone or download the repository, and open a command prompt in the the downloaded directory - `spwebapp`.
2. Run

   ```python -m pip install -r requirements.txt```

3. Download and install MS SQL Server on your machine. After installation, you will get a prompt to install SQL Server Management Studio, install it.
4. Open SSMS and connect to the SQL server. Open the following file in the downloaded directory with SSMS - /spwebapp/SPW/database/users_db.sql 
5. Execute the SQL query opened from the file above in SSMS and your sql database is created now.
6. Next, expand security in SSMS and create a login user with SQL Server Authentication and give permissions to the users_db to this user. Note down the credentials.
7. Right click your SQL connection in SSMS, select properties>security and select SQL Server and Windows Authentication Mode.
8. Open SQL Server Configuration manager, go to SQL Server Network Configuration>Protocols for MSSQL Server and open TCP/IP properties.
9. Enable TCP/IP. Click on IP Addresses tab, navigate to 127.0.0.1 and enable it. Click ok.
10. Click on SQL Server Services and restart the SQL Server (MSSQLSERVER) Service.
11. Edit the .ini file and put in the credentials you created in SSMS. 
12. Browse to /spwebapp/SPW/ and Run

   ```python -m main.py```

13. Your online shop is up and running. Open a browser and navigate to 127.0.0.1:8000 and start browsing.

## License
[MIT License](https://github.com/amiket23/spwebapp/blob/main/License)
