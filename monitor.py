import os
import time
import requests
from requests.exceptions import HTTPError
import json
from datetime import datetime

URL = "http://127.0.0.1:8000/shearerpos"
headers = {
  'Content-Type': 'application/json'
}

def where_json(file_name):
	return os.path.exists(file_name)

# check if the shearer is working by comparing it's last emit. If last emit more than 10 seconds, then error.
def statusCheck(timestamp, now):
	timestamp = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S.%f")
	diff = (now-timestamp).seconds
	if (diff > 10):
		return "ERROR"
	return "OK"

# add the data to the database
def addData(res, now, offline = False):
	with open("sample.json") as f:
		data = json.load(f)

		if offline:
			status = "OFFLINE"
			res['time'] = str(now)
		else:
			status = statusCheck(res['time'], now)

		if status == "ERROR" or offline:
			res['position'] = None

		res['status'] = status
		data["positions"].append(res)
		f.close()

	with open("sample.json", "w") as f:
		json.dump(data, f)
	return


def main():
	while True:
		now = datetime.now()
		try:
			r = requests.get(url = URL, headers= headers)
			res = json.loads(r.content.decode('utf-8'))
			print("Status: ",r.status_code, " Response: ",res)
			addData(res, now)
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')
		except Exception as err:
			print(f'ERROR: Maybe the Shearer API is not online/failed')
			addData({}, now, True)
		else:
			pass

		time.sleep(5)

if __name__ == "__main__":
	if where_json('sample.json'):
		pass
	else:
		dictionary ={
				"positions" : []
		}
				
		with open("sample.json", "w") as outfile:
				json.dump(dictionary, outfile)

	main()