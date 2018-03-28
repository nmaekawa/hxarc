#!/bin/bash -e

#
# this is an example for the script wrapper
#

input_file=${1}
input_dir=$(dirname ${1})
input_id=$(basename ${input_dir})  # assumes input file has a unique parent dir

echo "***** untar/ungzip input file ${input_file}"
# untar uploaded file
tar xzf ${input_file} -C ${input_dir}

echo
echo "***** about to process input file ${input_file}"

# create tmp result location
result_dir=/tmp/${input_id}/result
mkdir -p ${result_dir}

# here is where the script should be called
# pretend to do some processing and generate output
for file in $(find ${input_dir} -name "*.json" -print)
do
    cp $file ${result_dir}
done

echo "***** generating tar.gz"
echo

cd /tmp/${input_id}
tar cvzf ${input_dir}/result.tar.gz result

echo "***** all done"

