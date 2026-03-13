import urllib.request

url = "http://localhost:8000/metrics"
resp = urllib.request.urlopen(url)
data = resp.read().decode('utf-8')

with open("metrics_output.txt", "w", encoding="utf-8") as f:
    f.write(data)
