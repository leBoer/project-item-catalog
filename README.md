# Introduction
This application is a project submitted for the Udacity Full Stack Nanodegree. It is an item catalog where a registered user can add items to already defined categories. Users will also be able to delete and edit their items, but not items created by other users. I have chosen to only include facebook sign in, so if you don't have a facebook account, you'll not be able to add any items.

There are also a few JSON endpoints included:
 - **/catalog/users/json** (*All users*)

 - **/catalog/categories/json** (*All categories*)

 - **/catalog/items/json** (*All items*)

 - **/catalog/item/{{item_id}}/json** (*A specific item*)

 - **/catalog/json** (*All categories with corresponding items*)

 # Getting Started

 1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html)
 2. Clone this repository to a folder on your computer
 3. Use your terminal and navigate to the folder that contains the "Vagrantfile" (included in the clone)
 4. Launch the Vagrant VM by typing "vagrant up" (might take a few minutes)
 5. Log into the VM by typing "vagrant ssh"
 6. Get to the shared folder by typing "cd /vagrant"

 **Now your VM is up and running, and you have access to the files. Let's start running the application:**

 1. Initiate the database by running "python database_setup.py"
 2. Populate the database by running "python populatedb.py"
 3. Start the local server by running "python application.py"
 4. The project is now available through [http://localhost:8000](http://localhost:8000)