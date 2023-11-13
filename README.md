1. This is a mixed team work project for Course ECE568 in Duke University
2. This repo contains the code for UPS side and Amazon side
3. The aim for this project is to create a UPS-Amazon pair to simulating the Good Delivering Process in the real world.
4. In the real world, once a user purchase in amazon, amazon will notify its partener UPS related information, UPS will be responsible for schedule good delivery with its driver , once finished, the amazon will be notified as well as the user, then a whole process is finished.
5. Our Project simulates this process, and the amazon and the UPS side use Google Protocol Buffer message to communicate with each other.
6. To run the whole project, please cd mini_amazon to run the amazon side first with the instructions shown in README.md
7.After you have successfully run mini_amazon
then cd back to the top level directory,
then cd docker_deploy, run sudo docker-compose up
A Few Important things for reminder to run the project:
1. Please Make sure you have installed the service of docker and postgresql in your linux system, if possible, you may need to install other related service.
2. Please make sure you have cleared all docker images and container before running the project, for example, you may need run sudo docker-system prune
3. Please reminder to change the port, in mini_amazon/web-app/README.md, there is a clear instruction on how to change the port for amazon, after you have the port for amazon, please cd back to the UPS directory, Go to docker_deploy/back-server-python/upsserver.py, line 603, 604 change the ip(localhost if you run together) and the port(the port you decided to use for amazon)
Enjoy the project! you should first puchase order in amazon and to check the order status in UPS side.
Please see score and feedback proof via:
https://drive.google.com/drive/my-drive?hl=en
