#!/usr/bin/env bash
set -e
set -x

yaml_path=$1
yaml_key=$2
new_release_version=$3

if [ -z "${yaml_path}" ]; then echo "'yaml_path (\$1)' is not set, exiting"; exit 1; fi
if [ -z "${yaml_key}" ]; then echo "'yaml_key (\$2)' is not set, exiting"; exit 1; fi
if [ -z "${new_release_version}" ]; then echo "'new_release_version (\$3)' is not set, exiting"; exit 1; fi

yq "${yaml_key} = \"${new_release_version}\"" ${yaml_path} > /tmp/new.yaml
if grep -q ${new_release_version} /tmp/new.yaml; then
    echo 'Version update succeed, new:'
    grep ${new_release_version} /tmp/new.yaml
else
    echo 'Version update failed, exiting'
    exit 1
fi

diff -U0 -w -b --ignore-blank-lines ${yaml_path} /tmp/new.yaml > /tmp/version.diff || true
patch ${yaml_path} < /tmp/version.diff
