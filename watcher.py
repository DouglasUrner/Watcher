import os
import subprocess

# watcher.py
#
# Manage process of watching a set of websites / pages for changes.
#
# The underlying method is inspired by a simpler version by Gaelan
# Steele for watching letting agent websites in a university town. Her
# work, and mine is inspired by Simon Willison's post:
#
# https://simonwillison.net/2020/Oct/9/git-scraping/

watcher_lib=f"../Watcher/lib"

# Collect a list of URLs and local paths of the pages we're watching.
rv = subprocess.run(        # Get list of pages to watch.
    [
        "python3", f"{watcher_lib}/urlgen.py",
        "policies"
    ],
    capture_output=True,
    text=True
)
if rv.returncode != 0:
    print(f"Error: unable to get URLs: urlgen returned: {rv.returncode}")
else:
    #targets = rv.stdout.splitlines()
    targets = rv.stdout

# Process targets
rv = subprocess.run(        # Get list of pages to watch.
    [
        "python3", f"{watcher_lib}/process.py",
        targets
    ],
    text=True
)