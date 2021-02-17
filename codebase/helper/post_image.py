# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 17:59:57 2021

@author: Jannik
"""

import base64
import requests

# duration in seconds (default is 12 hours)
def image_comment(token, file, duration=43200):
    
    # post image to imgbb
    with open(file, "rb") as file:
        url = "https://api.imgbb.com/1/upload"
        
        print(file)
        
        payload = {
            "key": token,
            "image": base64.b64encode(file.read()),
            "expiration": str(duration)
        }
        
        # extract image url
        res = requests.post(url, payload)
        url = res.json()["data"]["url"]
        comment = "Preview of submitted forecast: \n ![]({})".format(url)
        
        return comment