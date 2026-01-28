Version 1.0:

Noteable additions:
1) Database initialised.
2) Tables created.
3) All classes and enums defined.
4) Login loop created.

Use Guide for Users:
Currently there is little functionality which can directly be used by the end-user.
Users are able to continuously login. See the guide below for instructions on how to do this.

Login Guide:
1) Start the program by running main.py.
  
2) Look at the console. You will be greeted with a prompt asking you to enter your username and password. Currently there is one admin which is hard coded into the database.
   The login details are as seen:
   username: admin
   password: admin123
   
3) Apon entering these details, you will be logged in successfully. You can confirm this by seeing a custom message greeting you.

   If you enter the wrong credentials, you will be prompted with a useful error message.
   If you have entered an invalid username, the error message will read: "[ERROR] User not found."
   If you have entered an invalid password, the error message will read: "[ERROR] Incorrect Password"

Currently, as there is no other functionality, succcessful login will simply loop back around, prompting you to login again. In later versions, successful login will grant access into the system, showing you the user menu.
