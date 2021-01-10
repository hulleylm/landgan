import requests

api_key = open("config.txt", "r", encoding="utf-16").read()

zoom = "10"
center = "40.714%2c%20-73.998"

url = "https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + zoom + "&size=400x400&key=" + api_key

r = requests.get(url)
f = open('output.png', 'wb')
f.write(r.content)
f.close()
