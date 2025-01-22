#! /bin/sh

# Watch a websites for changes by downloading pages and archiving them
# in a git repository. Push notification of changes.

for url in $(cat urls.txt); do
    echo -n '>>>' $url:
 
    dir=out/$(./pathogen.sh $url)
    name=$(date -Iseconds)
    path=$dir/$name
    mkdir -p $dir

    curl -m 60 -A "Watcher/0.1; (watcher@fastmail.org)" $url > $path
    if ! prettier --write --parser html $path; then
        tidy -mi --force-output true -ashtml --drop-empty-elements no --drop-empty-paras no --fix-style-tags no --join-styles no --merge-emphasis no --tidy-mark no $path
        prettier --write --parser html $path
    fi

    if [[ -f process/$name ]]; then
        cp $path tmp
        process/$name <tmp >$path
        rm tmp

        prettier --write --parser html $path
    fi
    echo
done

# https://simonwillison.net/2020/Oct/9/git-scraping/
git add -A
timestamp=$(date -u)
git commit -m "Latest data: ${timestamp}" || exit 0

curl -s \
    --form-string "t=$(grep '^Name:' ./sites-group.txt | sed s.NAME:\ ..)" \
    --form-string "m=$(git diff --stat=999 'HEAD^1..HEAD')" \
    --form-string k=$(cat ~/.config/pushsafer_key) \
    https://www.pushsafer.com/api

git push origin main