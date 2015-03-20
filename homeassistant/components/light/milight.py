"""
Support for Milight/LimitlessLED lights.

Configuration:

light:
    platform: milight
    host: YOUR_MILIGHT_IP
    port: YOUR_MILIGHT_PORT (defaults to 8899)
    groups:
        1:
            name: Living Room
            types:
              - rgbw
              - rgb
              - white
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

"""
TODO:
    fix colors, hue seems to be off; perhaps hsv will work?
    consider using wifileds library instead, not compatible with python3...
    get colors working, needs patch to limitlessled library
    add effects (if above is done)
"""

import logging
import socket
from math import ceil
from datetime import timedelta
from urllib.parse import urlparse

from homeassistant.loader import get_component
import homeassistant.util as util
from homeassistant.helpers.device import ToggleDevice
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_XY_COLOR, ATTR_RGB_COLOR)
_LOGGER = logging.getLogger(__name__)
try:
    from milight import color_from_rgb
except:
    _LOGGER.exception("Error while importing dependency milight.")




def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """ Gets the Hue lights. """
    try:
        # pylint: disable=unused-variable
        import milight  # noqa
    except ImportError:
        _LOGGER.exception("Error while importing dependency milight.")

        return

    host = config.get(CONF_HOST, None)
    port = config.get(CONF_PORT, 8899)

    try:
        bridge = milight.MiLight({'host': host, 'port': port})
    except ConnectionRefusedError:  # Wrong host was given
        _LOGGER.exception("Error connecting to the milight bridge at %s:%d", host, port)

        return

    groups = []
    
    infos = config.get('groups')
    
    for group_id in range(1,5): #only 4 groups per bridge
        info = infos.get(group_id, {'name': 'Group {}'.format(group_id)})
        if info.get('exclude', False):
            continue
        types = info.get('types', ['rgbw'])
        light = milight.LightBulb(types)
        groups.append(MiGroup(group_id, info, bridge, light))

    add_devices_callback(groups)


class MiGroup(ToggleDevice):
    """ Represents a Milight Group """

    def __init__(self, group_id, info, bridge, light):
        self.group_id = group_id
        self.info = info
        self.bridge = bridge
        self.light = light

    @property
    def unique_id(self):
        """ Returns the id of this MiLight """
        return "{}.{}".format(
            self.__class__, self.info.get('name'))

    @property
    def name(self):
        """ Get the mame of the group. """
        return self.info.get('name')

    @property
    def state_attributes(self):
        """ Returns optional state attributes. """
        attr = {}

        if self.is_on:
            attr[ATTR_BRIGHTNESS] = self.info.get('brightness', 255)
            attr[ATTR_XY_COLOR] = self.info.get('xy', None)

        return attr

    @property
    def is_on(self):
        return self.info.get('on', False)

    def turn_on(self, **kwargs):
        """ Turn the specified or all lights on. """
        self.bridge.send(self.light.on(self.group_id))
        self.info['on'] = True

        if ATTR_BRIGHTNESS in kwargs:
            level = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
            self.bridge.send(self.light.brightness(level, self.group_id))
            self.info['brightness'] = kwargs[ATTR_BRIGHTNESS]

        if ATTR_XY_COLOR in kwargs:
            self.info['xy'] = kwargs[ATTR_XY_COLOR]
            
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            color = color_from_rgb(*rgb)
            if color < 0:
                self.info['on'] = False
            self.bridge.send(self.light.color(color))

    def turn_off(self, **kwargs):
        """ Turn the specified or all lights off. """
        self.bridge.send(self.light.off(self.group_id))
        self.info['on'] = False

    def update(self):
        pass
