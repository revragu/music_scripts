#!/bin/bash

  source_file="$1"
  md5=$(python3 getTags.py -i "$source_file" | md5sum | cut -d' ' -f1)
  printf "%s\t%s\n" "${md5}" "${source_file}"
