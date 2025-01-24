import csv
import os
import sys

from string import Template

# Generate a list of URLs to retrieve.
# 
# Expects:
# - states-and-territories.txt: top level divisions
# - <state>/districts.txt: one per state, districts & base URL components
# - argv[1]: basename of the file listing objects to retrieve
#   the basename of the file is used as the directory where the
#   files are saved

# TODO
# - Reorganize configuration so that each district has a config file that
#   gives the base path for each type of objects, something like:
#   policies|dir_a/dir_b/dir_c
#   procedures|dir_a/dir_d
# - Log to a file or syslog

with open('states-and-territories.txt', 'r') as states:
    states_reader = csv.reader(states, delimiter='|')

    for state in states_reader:

        if state[0].startswith('#') or not state[0]:
            continue
        print(state[0] + ' >>>', file=sys.stderr)

        # Check that state directory exists.
        if not os.path.isdir(state[0]):
            # Directory didn't exist, create it and copy in boilerplate
            # files. Then issue warning and continue.
            os.mkdir(state[0])
            continue
        elif not os.path.isfile(state[0] + '/districts.txt'):
            # List of school districts is missing,
            # issue warning and continue.
            print(f"Error: {state[0]}/districts.txt not found", file=sys.stderr)
            continue
        
        elif not os.path.isfile(state[0] + '/' + sys.argv[1] + '.txt'):
            # List of objects to retrieve is missing,
            # issue warning and continue.
            print(f"Error: {state[0]}/{sys.argv[1]}.txt not found", file=sys.stderr)
            continue

        with open(state[0] + '/districts.txt','r') as districts:
            districts_reader = csv.reader(districts, delimiter='|')
            line = 0 # Line count for error messages
            for district in districts_reader:
                line += 1

                # Check the completness of the district record.
                if district[0].startswith('#'):
                    continue
                elif not district[1]:
                    print(f"Error: missing district name at line {line} in {state[0]}/districts.txt", file=sys.stderr)
                    continue
                elif not district[4]:
                    print(f"Error: missing district website at line {line} in {state[0]}/districts.txt", file=sys.stderr)
                    continue
                elif not district[5]:
                    print(f"Error: missing district policy root at line {line} in {state[0]}/districts.txt", file=sys.stderr)
                    continue

                # Construct the name of the district directory and check that
                # it exists. Create it if it does not.
                district_dir = state[0] + '/' + district[1].replace(" ", "_").lower()
                if not os.path.isdir(district_dir):
                    os.mkdir(district_dir)

                # Construct the path to the target directory and check that it
                # exists. Create it in it does not.
                target_dir = district_dir + '/' + sys.argv[1]
                if not os.path.isdir(target_dir):
                    os.mkdir(target_dir)

                # Construct the URL of the object we're going to retrieve.

                # Presumed values for districts.txt
                website = district[4]
                document_root = district[5]
                default_template = '{id}'

                # Check for map.txt file and overwrite defaults if needed, at the same time
                # we also count the number of entries in the map file so that we don't need
                # to reprocess the map if there is only the default entry.
                #
                # XXX: allow CMS specific map files, e.g., map-foo.txt

                mapfile = target_dir + '/map.txt'
                if os.path.isfile(mapfile):
                    map_entries = 0
                    with open(mapfile, 'r') as map:
                        map_reader = csv.reader(map, delimiter='|')

                        # Get the default map
                        for mapping in map_reader:

                            if not mapping[0].startswith('#'):
                                map_entries += 1

                            if mapping[0].startswith('*'): # XXX - should be exact match

                                # Don't count the default entry.
                                map_entries -= 1

                                map_path = mapping[1]
                                map_template = mapping[2]

                                if map_path.startswith('http://') or mapping[1].startswith('https://'):
                                    # Map specifies full document root.
                                    root_url = map_path
                                elif map_path.startswith('/'):
                                    # Map specifies document root relative to district website.
                                    root_url = "https://" + website + map_path
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                                elif map_path:
                                    # Presumably a directory to append to the district document root.
                                    root_url = "https://" + website
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                                    root_url += document_root
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                                    root_url += map_path
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                                else:
                                    root_url = "https://" + website
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                                    root_url += document_root
                                    if not root_url.endswith('/'):
                                        root_url += '/'
                            
                                if map_template:
                                    default_template = map_template

                # XXX: check for and process a map-local.txt

                with open(state[0] + '/' + sys.argv[1] + '.txt') as targets:
                    targets_reader = csv.reader(targets, delimiter='|')

                    for target in targets_reader:
                        if target[0].startswith('#'):
                            continue
                        target_name = target[0]
                        if map_entries:
                            # Reopen map(s) and search for a map for this target.
                            # XXX - this should be a function that takes the target (or '*') as
                            #       its argument.
                            mapfile = target_dir + '/map.txt'
                            if os.path.isfile(mapfile):
                                with open(mapfile, 'r') as map:
                                    map_reader = csv.reader(map, delimiter='|')
                                    template = default_template
                                    for mapping in map_reader:
                                        if mapping[0].startswith('#') or mapping[0].startswith('*'):
                                            continue
                                        #print(f"Target: {target_name} Mapping: {mapping[0]}")
                                        if mapping[0].startswith(target_name): # XXX should be exact
                                            template = mapping[2]
                        # XXX - this isn't complete, assumes how WA does things and is only based
                        #       on a few districts.
                        t = Template(template)
                        target_name = t.substitute(id=target[0], sname=target[1].lower().replace(' ', '-'))
                        url = root_url + target_name

                        path = f"{target_dir}/{target[0]}"

                        print(f"{url}|{path}")
