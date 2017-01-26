#!/usr/bin/env python3
# version 0.1:
# - Create POC for making reflecting changes in notification settings

import subprocess
import os
from xml.etree.ElementTree import parse, dump, Element

if __name__ == '__main__':
    # download configuration
    output = subprocess.check_output(
        'defaults export com.apple.ncprefs - > com.apple.ncprefs', shell=True)

    ncprefs = parse('com.apple.ncprefs')
    all_dict = ncprefs.findall('.//array/dict')
    for d in list(all_dict):

        # Reshuffle <dict> into the following format:
        #     {id: (value,type)}
        #
        # Example of <dict> element in exported defaults
        # <dict>
        #     <key>bundle-id</key>
        #     <string>_SYSTEM_CENTER_:com.apple.battery-monitor</string>
        #     <key>flags</key>
        #     <integer>535</integer>
        # </dict>

        # 1. Arrange into format
        k = None
        processing_id = None
        processing_value = None
        for c in list(d):
            if k is None:
                # key
                k = c.text
            else:
                # value
                if k == 'bundle-id':
                    processing_id = c.text
                elif k == 'flags':
                    processing_value = c.text
                else:
                    raise Exception(
                        'Unknown key was found in <dict>: ' + k)
                k = None
            d.remove(c)

        # 2. Change value (Silent all notification)
        if not processing_id.startswith('_SYSTEM_CENTER_:'):
            processing_value = str(int(processing_value) & ~ 4)

        # 3. Assign back to d
        subelement = Element('key')
        subelement.text = 'bundle-id'
        d.append(subelement)
        subelement = Element('string')
        subelement.text = processing_id
        d.append(subelement)
        subelement = Element('key')
        subelement.text = 'flags'
        d.append(subelement)
        subelement = Element('integer')
        subelement.text = processing_value
        d.append(subelement)

    # export configuration
    ncprefs.write('com.apple.ncprefs', encoding='UTF-8', xml_declaration=True)
    output = subprocess.check_output(
        'defaults import com.apple.ncprefs - < com.apple.ncprefs', shell=True)

    # cleanup
    os.remove('com.apple.ncprefs')

    subprocess.check_call('killall NotificationCenter', shell=True)
    subprocess.check_call('killall usernoted', shell=True)
