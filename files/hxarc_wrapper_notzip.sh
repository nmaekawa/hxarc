#!/bin/bash -e

#
# this is an example for the script wrapper
#

input_file=${1}
input_dir=$(dirname ${1})
input_id=$(basename ${input_dir})  # assumes input file has a unique parent dir

# subproc's pkg version, in this case using django
if [ ${1} == 'version_only' ]
then
    SCRIPT_VERSION=$(pip show django | grep 'Version' | cut -d ' ' -f 2)
    echo $SCRIPT_VERSION
    exit 0
fi

echo
echo "***** about to process input file ${input_file}"

# here is where the subproc script should be called
# pretend to do some processing and generate output
for file in $(find ${input_dir} -name "*.csv" -print)
do
    cp $file ${input_dir}/result.json
done

echo "***** all done"

