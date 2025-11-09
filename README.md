# busStop_teller
Bus Stop Arrival Display using Raspi Zero and Epaper Display

<img width="810" height="568" alt="Screenshot 2025-11-08 at 8 40 13 PM" src="https://github.com/user-attachments/assets/194d4916-e3c4-4231-a611-08ba15844ef4" />



youtube link here

instructables link


Materials

-Waveshare 7.5in (or any other size) Epaper Display : https://www.waveshare.com/7.5inch-e-paper-hat-b.htm 

-Raspberry Pi Zero W (or other vairation)

-HDMI, keyboard, mouse, power cords

-3D Printer + Filament

-2x4mm Screws (6) 



1. Preperation + Connection

   If this is your first time working with a Raspberry Pi I would really recommend downloading the Desktop version of Raspbian to get some intuition for whats going on. To connect to our pi so we dont have to constantly have a keyboard, mouse, and external monitor connected well download vnc and setup ssh to our pi. Both methods work but I personally prefer ssh. These steps will especially come in handy if you have a raspberry pi zero with only one available usb connection.
   The next steps are assuming you have the RPI 32 bit lite installed.
   
   a) For SSH run the following commands in pi terminal

   >hostname -I

   >sudo raspi-config

   interface options -> SSH (and VNC if you want) -> enable -> finish

   on your PC terminal type ssh pi@"ip adress of pi" : (also change the pi before the @ if your local host name is different)

   b) For VNC do the following
   
   >sudo apt update
   
   >sudo apt upgrade
   
   >sudo apt install -y realvnc-vnc-server realvnc-vnc-viewer
   
   >sudo raspi-config
   
   interface options -> VNC -> enable ->finish
   
   >sudo systemctl enable --now vncserver-x11-serviced.service
   
   >hostname -I
   
   on you PC open up the VNC software and type in your IP to connect
   
   c)Connect Epaper ribbons to SPI controller and then connect SPI controller ribonns to driver. Make sure on the SPI controller modes are on the correct ones. For 4" displays and up the Display Config Switch should be on A=3R. Smaller displays should be set to 0.47R. The Interface Config switch should be set to 0 = 4-line SPI (this is the correct mode for an Pi). 

   d)Connect 40 Pin Header to Raspberry Pi pins, making sure they align on top of each other, almost like stacking.

   Final Connection should look like this: <img width="419" height="375" alt="Screenshot 2025-11-08 at 3 51 19 PM" src="https://github.com/user-attachments/assets/03d366e5-0eeb-480a-96f9-c8729dee2423" />

3. Testing
   
   First we must make sure that everything is working correctly by running Waveshare's testing code. This essentially just flashes a couple images to the display and if everything is connected properly and no issues happened you should be able to see those previews.
   
   The link to the manual: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT
   
   The link to the Raspberry Pi connected Display Manual: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual#Working_With_Raspberry_Pi

   Run the following commands:
   >sudo raspi-config nonint do_spi 0
   
   >sudo apt update
   
   >sudo apt install -y python3-pip python3-pil python3-spidev python3-rpi.gpio git
   
   >cd ~
   git clone https://github.com/waveshare/e-Paper.git
   
   >cd ~/e-Paper/RaspberryPi_JetsonNano/python/examples
   sudo python3 epd_7in5_V2_test.py

   If everything worked properly you should see a few images flash and the epaper display refresh a couple times before turning off.
   Note: Change the test depending on your epaper display size and specifications.
   

5. Customization
   
   To add the bus stop code, theres some stuff we have to do first. Before anything we have to get an API key from the AC Transit website. I am using AC Transit because it's just because its the buses I use specifically but most public transit organizations will have their own website where you can get an API key and gather data. Research online for your case.
   To get the AC Transit API go here: https://api.actransit.org/transit, register and copy your api to be pasted into the busstop.py code.

   The python scripts essentially calls the AC Transit API, uses Pillow to draw the image, saves that image as a png and then pushes it to the epaper display. Updates every 60 seconds and sorts by soonest arrival.

   Before running the code, you have to
   
   a)insert your own API in place of API_KEY
   
   b)alter the routes to your own. To do this go to Google Maps, click on the bus stop you want to watch and get the ID. You can then change the description of the bus stop and also what you want it labeled as.
   
   c)edit the epaper image in the "draw_display" function if you would like

   After you have finalized your code you have to make it run on the pi. //TODO: explain this
   
7. Assembly
   I 3D modeled a frame design for my wall, its pretty standard and is designed for one wall thumbtack but has a wide enough base to be oriented upright on a desk.

   things the print needs to have:
   -thumbtack slot like link
   -filet on side for wire
   -indent for epaper display
   -cover for display that attached via screws to the ocver
   -pillars for connector and pi+hat with 2mm screws
   -lip for ribbon
   
   -print 3d printed frame parts from my makerspace for one for wall mount, cad this: https://www.thingiverse.com/thing:3996613 
   -Or: A really great Desktop design by user Cybernetic on Thingiverse : https://www.thingiverse.com/thing:4807262

Thats it. Thanks!
