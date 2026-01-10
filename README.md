# MY HOME-ASSISTANT CONFIG


Hardware:  
 - Raspberry-Pi 5
 - 128GB SSD
 - TI Zigbee Dongle (CC2652P)
 - 5A Power Supply   

<img src="images/hardware.png" width=60%>
<br>
<br>
<br>

Zigbee Devices  
<img src="images/zigbee_devices.png" width=60%>

<br>
<br>

### Fil Pilote Devices  

Principes  

<img src="images/fil_pilote.png" width=60%>
<br>
<br>

Tuya or Aubess 2 Gangs switch modified with 2 diodes  

<img src="images/Diodes_FP.png" width=60%>

<br>
<br>
<br>

# Cards  

### Home Page  
<img src="images/temp_hum.png" width=60%>  

### Mountains Wheater 
<img src="images/montagne.png" width=60%>  

### Electric Heaters  
<img src="images/heaters.png" width=60%>

### Lights  
<img src="images/lights.png" width=60%>

### Power Meter From Linky
<img src="images/linky.png" width=60%>

### Doors Sensors
<img src="images/doors.png" width=60%>

### Batteries Levels
<img src="images/batteries.png" width=60%>

### Network Info
<img src="images/network.png" width=60%>
<br>
<br>
<br>

## Add-ons used

<img src="images/add-ons.png" width=80%>

## Integrations used

<img src="images/integrations.png" width=80%>


# Advance SSH & Web terminal

In order to have allow execution of shell_command 
Create a directory inside /config  
```
cd config 
mkdir .ssh 
```
copy inside the directory your ssh public key __ssh_host_rsa_key.pub_ located in the directory __data__  
Add also the key also inside the add-ons configuration  


# Link and notes

Cool link for yaml essential:  https://yamline.com/tutorial/
a good home-assistant config : https://github.com/basnijholt/home-assistant-config/tree/master


