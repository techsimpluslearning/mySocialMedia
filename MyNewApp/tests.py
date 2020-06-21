from django.test import TestCase

import urllib
import urllib.request as urllib2

authkey = "232419AGxejpXap5eeb621aP1"
mobiles = "9893762256, 9001411745"
sender = "TCHSIM"
msg = 'Hello, this is test sms'
route = '4'

Dict = {
    "authkey":authkey,
    "mobiles":mobiles,
    "message":msg,
    "sender":sender,
    "route":route
}

url = "http://api.msg91.com/api/sendhttp.php"
postData = urllib.parse.urlencode(Dict)
postData = postData.encode("ascii")
req = urllib2.Request(url, postData)
resp = urllib2.urlopen(req)

op = resp.read()