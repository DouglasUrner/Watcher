#! /bin/sh

for url in $(cat urls.txt); do
    echo '>>>' $url
    #name=$(echo $url | sed s./._.g)
    #path=out/$name
    dir=$(./pathogen $url)
    name=$(date -Iseconds)
    path=$dir/$timestamp
    mkdir -p dir
    curl -m 60 -A "GaelanSteeleBot/1.0; (+https://gaelan.me)" $url > $path
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
done

# https://simonwillison.net/2020/Oct/9/git-scraping/
git add -A
timestamp=$(date -u)
git commit -m "Latest data: ${timestamp}" || exit 0

curl -s \
    --form-string "t=Letting Update" \
    --form-string "m=$(git diff --stat=999 'HEAD^1..HEAD')" \
    --form-string k=$(cat ~/.config/pushsafer_key) \
    https://www.pushsafer.com/api

git push origin main