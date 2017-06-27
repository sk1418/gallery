#!/bin/bash


if [[ $1 == "-d" ]]; then
	DRY="--dry-run"
fi

SRC="$HOME/Dropbox/书法/mine/"
rsync $DRY --ignore-existing -av "${SRC}精临练笔" "store/"
rsync $DRY --ignore-existing -av "${SRC}古诗文" "store/"
rsync $DRY --ignore-existing -av "${SRC}闲笔" "store/"
rsync $DRY --ignore-existing -av "${SRC}歌词" "store/"

if [[ $1 == "-d" ]];then
echo "============================================================================="
	echo "Dry run done"
	exit 0
fi
echo "============================================================================="
echo "Start creating gallery website..."
echo "============================================================================="
build.py -i
