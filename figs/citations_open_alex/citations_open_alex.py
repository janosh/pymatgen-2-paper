import matplotlib.pyplot as plt

import requests

# OpenAlex Work ID for the pymatgen paper
openalex_id = "w2015197254"
base_url = f"https://api.openalex.org/works?group_by=publication_year&per_page=200&filter=cites:{openalex_id}"



years = []

response = requests.get(base_url)
data = response.json()
years=[]
counts=[]
for year in data["group_by"]:
    years.append(year["key"])
    counts.append(year["count"])



# Reverse the order of the data
years.reverse()
counts.reverse()

# Plot the data
plt.figure(figsize=(10, 5))
plt.bar(years, counts)
plt.xlabel("Year")
plt.ylabel("Citations")
plt.savefig("citations_open_alex.pdf")