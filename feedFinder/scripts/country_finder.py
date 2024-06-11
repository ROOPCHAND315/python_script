import socket
from ip2geotools.databases.noncommercial import DbIpCity

def get_country_name(domain_list):
    country_names = []
    for domain in domain_list:
        try:
            ip_address = socket.gethostbyname(domain)
            response = DbIpCity.get(ip_address, api_key='free')
            country_names.append(response.country)
        except (socket.gaierror, ValueError):
            country_names.append("Unknown")
    return country_names

countryList = [
    'https://www.elcomercio.com/',
]

res = get_country_name(countryList)
print(res)
