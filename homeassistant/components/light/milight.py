"""
Support for Milight/LimitlessLED lights.

Configuration:

light:
    platform: milight
    wifi_receiver_ip: YOUR_MILIGHT_IP
    device_data:
        1:
            name: Living Room
        2:
            name: Bedroom
        3:
            exclude: true

VARIABLES:

wifi_receiver_ip
*Required
This is the IP address of your MiLight WIFI Receiver Controller. Port is not needed.


device_data
*Optional
This contains an array of info for each light group, 1-4. This can be used to 
set names for your groups or ignore them completely. If not specified, a group
will appear as 'Group #'.


These are the variables for the device_data array:

name
*Optional
This parameter allows you to override the name of your light group.


exclude
*Optional
This parameter allows you to exclude the specified group from homeassistant,
it should be set to "true" if you want this group excluded

"""
#WIP
