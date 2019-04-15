# Smart Greenhouse Management System

This project is a requirement for the Programming for IoT course at 
Politecnico di Torino.

Presentation Video:
https://youtu.be/Xf-MNAfASjQ

Explanation Video:
https://youtu.be/nBuABmgVjqA

## Features

This system uses:
* [CherryPy](https://cherrypy.org/) to build the web application
* [Freeboard](https://github.com/Freeboard/freeboard) as an IoT dashboard
* Freeboard [Highchart plugin](https://github.com/onlinux/freeboard-dynamic-highcharts-plugin)
* [Telepot](https://github.com/nickoala/telepot) as a framework for the telegram bot API.

The system features a dynamic menu page that updates as more devices connect. Please see the [explanation video](https://youtu.be/nBuABmgVjqA?t=640) for a demonstration.

## Required Fixes
Below is a list of some errors that need fixing:
* Change the catalog which defines devices connected in a way it doesn't use a dynamic key.
* Achieve more microservice structure by disconnecting the telegram bot API from the control strategies and make all communication go through the broker
* Adjust the MQTT-to-Web microservice to make it more robust.
