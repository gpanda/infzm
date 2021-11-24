#!/bin/bash - 
#==============================================================================
#
#          FILE: cronjob.sh
#
#         USAGE: ./cronjob.sh
#
#   DESCRIPTION: Cron script to download and email "The Economist" news
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Ren, Letian (), gpanda.next@gmail.com
#  ORGANIZATION:
#       CREATED: 11/26/2016 14:27:28
#      REVISION: ---
#==============================================================================

set -o nounset                              # Treat unset variables as an error

. rc

cd `dirname $0`
# Download the news
[ -f downloads/cookies ] && rm downloads/cookies
./fetch-news.sh
name=`ls -l ./downloads/latest | awk '{print $11}'`
mobi_name=$(basename "$name" .epub).mobi

# Convert from epub to mobi format
ebook-convert ./downloads/"$name" ./downloads/"$mobi_name"

# Email the news
calibre-smtp \
    -r smtp.yeah.net -e TLS -u camouflage314@yeah.net -p ren1et1an \
    --fork -o "$HOME/Maildir" \
    -s "$name" -a "./downloads/$mobi_name" \
    camouflage314@yeah.net "$RECEIVERS" "$MESSAGE"
cd -
