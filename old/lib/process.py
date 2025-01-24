import os
import subprocess
import sys

targets = sys.argv[1].splitlines()

# Process the targets: retrieve & add to GitHub repository.
for target in targets:
    print(target)
    
    fields = target.split('|')
    url = fields[0]
    file = fields[1]

    # Create the work directory if it doesn't exist.
    os.makedirs("work", exist_ok=True)

    # Copy the previous 

    continue

    # Retrieve the target URL and store into the target file.
    rv = subprocess.run( # wget
        [
            "wget2",
            "--timeout=60",
            "--user-agent='Watcher/0.1; (watcher@fastmail.org)'",
            url,
            f"--output-document={file}"
        ]
    )

    if rv.returncode != 0:
        print(f"Error: failed to retrieve '{file}': wget2 returned {rv.returncode}")
        continue
    else:
        # Force the retrieved file into a standard format using prettier,
        # and if necessary HTML tidy.
        #
        # Some districts return pages with timestamps or other features that change
        # every time you retrieve them. We only want to create new versions based on
        # actual changes of content -- but when there are actual content changes, we
        # want the new version to be unchanged by us. So:
        # - If we know that a site inserts "spurious" changes, make a copy of the
        #   old version of the page.
        # - Run it through prettier and if necessary tidy
        # - Edit it to remove the "noisy" stuff
        # - Run the new copy through prettier et all
        # - Edit it to remove the noise
        # - diff the two versions to see if there are changes
        # - If there are, copy the new version into the repository
        # - Then run git.
        # The version of the page in the repository will be exactly as it came from the
        # district website.
        rv = subprocess.run(   # 1st prettier run
            [
                "prettier",
                "--write",
                "--parser", "html",
                file
            ]
        )
        if rv.returncode != 0: # clean up with tidy & try again
            print(f"Initial prettier run failed on {file}: returncode = {rv.returncode}, running tidy")
            rv = subprocess.run(
                [
                    "tidy",
                    "-mi",
                    "--force-output", "true",
                    "-ashtml",
                    "--drop-empty-elements", "no",
                    "--drop-empty-paras", "no",
                    "--fix-style-tags", "no",
                    "--join-styles", "no",
                    "--merge-emphasis", "no",
                    "--tidy-mark", "no",
                     file
                ]
            )
            if rv.returncode != 0:
                print(f"tidy failed on {file}: returncode = {rv.returncode}")
                # XXX continue or add what we have to the repo?
            else:
                rv = subprocess.run(
                    [
                        "prettier",
                        "--write",
                        "--parser", "html",
                        file
                    ]
                )
                if rv.returncode != 0:
                    print(f"Second prettier run failed (after tidy) on {file}: returncode = {rv.returncode}")

    # Commit to repository and push to GitHub
    rv = subprocess.run(
        [
            "git",
            "add",
            "--all"
        ]
    )
    if rv.returncode != 0:
        # XXX - do anything else? When in the return value not 0?
        #       at the very least this will warn us if git isn't on
        #       our path.
        print(f"Error: 'git add --all' returned {rv.returncode}")
    rv = subprocess.run(
        [
            "git",
            "commit",
            f"--message=Latest version of {os.path.basename(file)}"
        ]
    )
    if rv.returncode != 0:
        print(f"{os.path.basename(file)} unchanged")
        continue
    else:
        rv = subprocess.run(
            [
                "git",
                "push",
                "origin" 
            ]
        )