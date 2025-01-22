import csv
import sys

with open(sys.argv[1] + 'districts.txt','r') as districts:
    districts_reader = csv.reader(districts, delimiter='|')

    for district in districts_reader:
        if district[0].startswith('#') or not district[5]:
            continue
        root_url = "https://" + district[4]
        if not root_url.endswith('/'):
            root_url += '/'
        root_url += district[5]
        if not root_url.endswith('/'):
            root_url += '/'

        with open(sys.argv[1] + 'policies.txt') as policies:
            policies_reader = csv.reader(policies, delimiter='|')

            for policy in policies_reader:
                if policy[0].startswith('#'):
                    continue
                url = root_url + policy[0]

                print(url)
