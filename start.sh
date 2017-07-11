#!/bin/bash


if [[ $1 == "-d" ]]; then
	DRY="--dry-run"
fi

SRC="$HOME/Dropbox/书法/mine/"
rsync $DRY -ignore-existing --delete-after --exclude="thumbnail/" -a "${SRC}精临练笔" "store/"
rsync $DRY -ignore-existing --delete-after --exclude="thumbnail/" -a "${SRC}古诗文" "store/"
rsync $DRY -ignore-existing --delete-after --exclude="thumbnail/" -a "${SRC}闲笔" "store/"
rsync $DRY -ignore-existing --delete-after --exclude="thumbnail/" -a "${SRC}歌词" "store/"

#rsync $DRY -ignore-existing --delete -av "${SRC}精临练笔" "store/"
#rsync $DRY -ignore-existing --delete -av "${SRC}古诗文" "store/"
#rsync $DRY -ignore-existing --delete -av "${SRC}闲笔" "store/"
#rsync $DRY -ignore-existing --delete -av "${SRC}歌词" "store/"

if [[ $1 == "-d" ]];then
echo "============================================================================="
	echo "Dry run done"
	exit 0
fi
echo "============================================================================="
echo "Start creating gallery website..."
echo "============================================================================="
python build.py -i
git add . && git commit -am'add images' && git push
