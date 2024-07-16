#!/bin/bash
template_file=$1
# remove j2 extension
final_file="${template_file%.*}"
jinja2 $template_file > $final_file
rm $template_file