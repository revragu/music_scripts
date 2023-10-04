#!/bin/bash

  source_file="$1"
  md5=$(ffmpeg -i "$source_file" -map 0:a -c copy -f md5 - | grep -E "^MD5=" | sed -E "s/^MD5=//")
  printf "%s\t%s\n" "${md5}" "${source_file}"
