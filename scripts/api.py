#!/usr/bin/env python3

import requests

response = requests.get("http://api.github.com")
print(response)
