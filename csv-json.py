import csv
import json

# Open the CSV
f = open('C:\\workspace\\python\\isuf\\firstapp\\weatherHistory.csv', 'rU')
# Change each fieldname to the appropriate field name. I know, so difficult.
reader = csv.DictReader(f, fieldnames=("City", "Date", "Formatted Date", "Summary", "Precip Type", "Temperature (C)", "Daily Summary"))
# Parse the CSV into JSON
out = json.dumps([row for row in reader])
print("JSON parsed!")
# Save the JSON
f = open('weather.json', 'w')
f.write(out)
print("JSON saved!")
