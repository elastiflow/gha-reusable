#!/usr/bin/env bash
set -e

yaml_path=$1
yaml_key=$2
new_release_version=$3

if [ -z "${yaml_path}" ]; then echo "'yaml_path (\$1)' is not set, exiting"; exit 1; fi
if [ -z "${yaml_key}" ]; then echo "'yaml_key (\$2)' is not set, exiting"; exit 1; fi
if [ -z "${new_release_version}" ]; then echo "'new_release_version (\$3)' is not set, exiting"; exit 1; fi

paths=$(echo $yaml_path | tr ',' '\n')
keys=$(echo $yaml_key | tr ',' '\n')

update_yaml_key() {
	key=$2
	path=$1

	yq "${key} = \"${new_release_version}\"" "${path}" > /tmp/new.yaml
	if grep -q "${new_release_version}" /tmp/new.yaml; then
		echo 'Version update succeeded, new:'
		grep "${new_release_version}" /tmp/new.yaml
	else
		echo 'Version update failed, exiting'
		exit 1
	fi

	diff -U0 -w -b --ignore-blank-lines "${path}" /tmp/new.yaml > /tmp/version.diff || true
	patch "${path}" < /tmp/version.diff
}

for p in ${paths}; do
	for k in ${keys}; do
		update_yaml_key ${p} ${k}
	done
done
