The flask app was developed to be run on linux machine.

Linux CTF
========================


The "Linux CTF" is a [CTF]-like activity to encourage the student to work on their own to explore the [Linux] filesystem, navigating in and out of directories to find different files. 

---------

The Server
----

To prepare the server, you should run the [`bash`][bash] script with arguments to supply a path for the [sqlite3] database it will create and use, and supply the [JSON] file that includes the challenges and flags. So an example setup would look like:

```
sudo ./setup.sh -d /tmp/database.db -c linux_basic.json
```

Once the server has installed all the dependencies and set up the system, you can run the server with:

```
sudo python server.py
```

The server runs threaded, and typically tries to use a certificate to work with an [HTTPS] connection (so no one could try and listen for flags and passed aren't passed in the clear), but lately this has been giving me trouble.

If you would like to reconfigure how the server sets itself up (port number, use of [HTTPS], etc..), then modify the last line of the `server_base.py` file (which the `setup.sh` uses to build off of).


---------------


The Client (End-User)
------------------

The client (the student, in this case) should have access to the repository but they should just run the initial `flags` file to set up the game. This is a simple [`bash`][bash] script that creates all the `FINDME.txt` files with the flags to submit (they are in plain text, but I don't expect any student to try and cheat and look at the flags in the script).

They should then be able to navigate to the web server and start to submit the flags, playing the Linux CTF!


-----------------
Poster for the SwanCTF Event
-----------------
![CTF Poster](https://user-images.githubusercontent.com/8989618/165846854-f674ded8-3c4e-4236-8b59-4fb01d22606b.png)
-----------------
