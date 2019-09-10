## WiFi Manager
The WiFi Manager is fully documented in the project WiKi. 
You can read the WiFi page Wiki [here](https://github.com/SamsungResearchUK-IoT-Meetup/projects/wiki/WiFi)

This document is here just to allow developers to quickly test this module in isolation. It forms a wrapper around the micropython
[network](http://docs.micropython.org/en/latest/library/network.html), [micropython schedule](http://docs.micropython.org/en/latest/library/micropython.html) and [pyb](http://docs.micropython.org/en/latest/library/pyb.html) library. It's used to monitor a WiFi connection and attempt to reconnect, if WiFi fails.
It will also retry when it initially connects to a new WiFi connection a default of 3 times - which is configurable. The WiFi manager also has a number of state variables and attributes mentioned later.

## PYB Library
The PYB Library is used to control timers on the microcontroller. This is configured to test a connection every 10 seconds. The timer object is stored in the
private object variable **_timer**

## Network Library
The Network Library is used to create a WLAN and WLAN Access Point (AP) objects. It is this that the WiFi manager monitors and controls. 
The WLAN AP object is stored in the private object variable _wifi_ap.
The WLAN object is stored in the private object variable _wifi.

# Creating a WiFi Manager
The WiFi Manager class is **Wifi_manager**. You can create the default object like:

```python
>>> from wifi.wifi_connect import *
>>> myWifi = Wifi_manager()
WiFi Manager bringing up wlan interface.
>>>

```

This instantiates your Wifi manager and creates a WLAN interface physically on the device.
You can find out status of the Wifi Manager and your Wifi Connection using the **status()** method:

```python
>>> myWifi.status()
(True, {'Connected': False, 'Access Point IP address': '0.0.0.0', 'Access Point Password': None, 'Access Point Name': None, 'Retries': 3, 
'Current IP address': '0.0.0.0', 'Started': 616853083, 'SSID name': None, 'Active monitor': False, 'Password': None, 'Access Point Connected': False})
>>>
```

# Connecting To A WiFi SSID
To connect to a WiFi network you need to supply the SSID and password of your network and use the **connect** method like this:

```python

>>> myWifi.connect('my-wifi-name', 'my-password')
Trying to connect to SSID: srbackup
Retrying to connect. Trying 0 of 3's
WiFi Manager is now monitoring the connection
(True, 'IP address is: 192.168.110.163')
>>> Connected on IP: 192.168.110.163
Connected on IP: 192.168.110.163
Connected on IP: 192.168.110.163
Connected on IP: 192.168.110.163

```
You will notice that appox every 10 seconds the WiFi manager will display the currently connected IP address.

# Disconnecting To A WiFi SSID
To disconnect to a WiFi AP you need to call up the **disconnect** method. Once the method is called the retry callback will fire one last time, but inform
the system it is no longer managing the WiFi network.

```python
>>>myWifi.disconnect()
(True, 'Wifi connection disconnected')
>>> Wifi Manager has stopped monitoring the connection

```

# Callback Function
To get the required behaviour of the system several things have to happen. However in a nut shell the timer is bound to a callback which checks the WiFi 
connection. If the connection is not up, it tries to reconnect. In detail the following steps happen:

- When the system connects using the **connect**, a timer is started and bound to a function **connect_callback**.
- The **connect_callback** uses the micropython schedule function which binds a member variable to be called when the CPU has done all other important tasks. This is done as the timer uses interrupts which stop memory being updated on the heap.
- The member variable **_bound_check_connection** is bound to the private method **__check_connection**. Since this is called when the heap can be accessed, this function does the WiFi connection checking.


# Setting Retries
The Wifi_manager can retry more than three times to connect to a WiFi network. To update the number of retires use:

   *myWifi.retries(n)* where 'n' is the number of retires.
   
To find out what the value is set to simply call the function with no attributes, like:

   *myWifi.retries()*
   
The example below shows real output:

```python
>>>myWiFi.retries(4)
(True, 'Retry set to 4 retries')
>>> myWifi.retries()
4
```


# Set Up As An Access Point
To setup an access point you can provide an access point name and password needed to connect using the method  **set_access_point** or the method will configure 
default values of:
- micropython
- test1234

   *myWifi.set_access_point()*
   
The WiFi manager will automatically manage your WiFi connection and bring down the connected WiFi if it exists.

The examples below shows real outpout:

```python
>>> myWifi.set_access_point()
(True, 'Access Point micropython created.')
>>> 
```

At this point you should see that there is an AP with 'micrppython' using your phone or laptop enabled with WiFi.

To deactivate the WAN AP you need to set an optional parameter to FALSE called **start_ap**. The **set_access_point** method has 3 optional parameters
which are:
- **ap_name**: The access point name is defaulted to 'micropython'.
- **ap_password**: The access point password is defaulted to 'test1234'.
- **start_ap**: This is defaulted to 'True', to deactivate your access point you need to set this to False.

An example is given below:

```python
>>> from wifi.wifi_connect import *
>>> myWifi = Wifi_manager()
WiFi Manager bringing up wlan interface.
>>> myWifi.status()
(True, {'Connected': False, 'Access Point IP address': '0.0.0.0', 'Access Point Password': None, 'Access Point Name': None, 'Retries': 3, 'Current IP address': '0.0.0.0', 'Started': 617119434, 'SSID name': None, 'Active monitor': False, 'Password': None, 'Access Point Connected': False})
>>> myWifi.set_access_point()
(True, 'Access Point micropython created.')
>>> DHCPS: client connected: MAC=24:00:ba:a9:07:07 IP=192.168.4.16
>>> myWifi.set_access_point(start_ap=False)
(True, 'Access Point deactivated')
```





