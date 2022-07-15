__author__ = 'chance'

import json
import os
import sys

import requests
# import tableau_api_lib
import xmltodict

sys.path.append('../modules')


def main():

    with open("test_xml.xml") as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()

        # generate the object using json.dumps()
        # corresponding to json data

        json_data = json.dumps(data_dict)
        print(json_data)

    server = "10ax.online.tableau.com"
    # version = "3.4"
    # site_id = "8e9d6a4d-25aa-4827-89e1-ebd97eaadc78"
    # contentUrl = "frantasydev764402"
    # user_id = "a5677c14-7196-41d3-afcc-49e876956369"

    # tableau_config = {
    #     'tableau_prod': {
    #         'server': 'https://10ax.online.tableau.com',
    #         'api_version': '3.4',
    #         'username': 'chance_st@yahoo.com',
    #         'password': 'Becton69!',
    #         'site_name': 'frantasydev764402',
    #         'site_url': 'frantasydev764402',
    #         'personal_access_token_name':'8e9d6a4d-25aa-4827-89e1-ebd97eaadc78',
    #         'personal_access_token_secret':'F0bBlF4zSKCNg1lPq7a7dw|YHbB1IFK2gNjBzIrFqeM2v7PynD6VgZ3|8e9d6a4d-25aa-4827-89e1-ebd97eaadc78',
    #         'cache_buster': '',
    #         'temp_dir': ''
    #     }
    # }

    tt = "AuPZjWQ5RoCeGdKyV-Edsw|LlO5azfWMPa9VGLGyYkfbO3QPy5cwqXq|8e9d6a4d-25aa-4827-89e1-ebd97eaadc78"
    tt = os.environ.get('TABLEAU', tt)

    print(tt)

    headers = {"X-Tableau-Auth": tt}

    url = f'https://{server}/api/3.4/sites'

    response = requests.post(url, headers=headers, json=data_dict)

    print("Status Code", response.status_code)
    print("JSON Response ", response.json())


    return


if __name__ == "__main__":
    main()
