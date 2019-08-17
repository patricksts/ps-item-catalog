Project Overview:

The Item Catalog project is an:
“application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.”
-udacity.com

In my case, I have created an app that is for cataloging various items that you might store in places of your choosing. You will be able to create the PLACE that you would like to store something and the THINGS that may be inside. You may also edit and delete the PLACES and THINGS that you have created.
You may view the PLACES and THINGS of other users, but you will not be able to alter them in any way.

User authentication is through Google.
Prerequisites and Setup: (Python 3 is necessary)

1.	Install VirtualBox and Vagrant – Instructions provided by udacity.com
VirtualBox
VirtualBox is the software that actually runs the VM. You can download it from virtualbox.org, here. Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.
Note: Currently (October 2017), the version of VirtualBox you should install is 5.1. Newer versions are not yet compatible with Vagrant.
Ubuntu 14.04 Note: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.
Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. You can download it from vagrantup.com. Install the version for your operating system.
Windows Note: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

Windows: Use the Git Bash program (installed with Git) to get a Unix-style terminal.
Other systems: Use your favorite terminal program

Run the virtual machine!
Using the terminal, change directory using the command [cd /vagrant]

2.	Clone my Github repository into your vagrant folder: (copy the link below directly into your “git clone” command.
a.	https://github.com/patricksts/ps-item-catalog.git

3.	Then type [vagrant up] to launch your virtual machine.
Once it is up and running, type [vagrant ssh] 
This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type exit at the shell prompt. To turn the virtual machine off (without deleting anything), type vagrant halt. If you do this, you'll need to run vagrant up again before you can log into it.
Now that you have Vagrant up and running type vagrant ssh to log into your virtual machine (VM). Change directory to the /vagrant directory by typing cd /vagrant. This will take you to the shared folder between your virtual machine and host machine.
Sharing files between the vagrant virtual machine and your home machine.
Be sure to change to the /vagrant directory by typing cd /vagrant before creating new files or pasting files that you want to be shared between your host machine and the VM.
	
4.	Run [pip install -r requirements.txt] in order to have all the necessary packages installed

5.	Run [python dbsetup.py] to initialize the database

6.	Run [python dbseed.py] to input some beginning data

7.	Run [python app.py]

8.	You will receive notification that the server is running on locahost:8000

9.	Open a browser and navigate to locahost:8000. You will see the list of places and options to click on the places to see what things are inside or log in. Login requires a google account. Once logged in you will be redirected to the places page where you may create, edit and delete your places and things. Enjoy!

*note for any steps including commands, omit the brackets when typing them 