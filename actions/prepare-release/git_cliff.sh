#!/usr/bin/env bash
set -e
set -f # Prevent globbing after variable substitution

while getopts ":c:t:i:e:" opt; do
  case $opt in
	c) config="$OPTARG"
	;;
	t) tag_prefix="${OPTARG:-'v'}"
	;;
	i) include_paths="${OPTARG:-''}"
	;;
	e) exclude_paths="${OPTARG:-''}"
	;;
	\?) echo "Invalid option -$OPTARG" >&2
	exit 1
	;;
  esac

  case $OPTARG in
	-*) echo "Option $opt needs a valid argument"
	exit 1
	;;
  esac
done

cliff_context=/tmp/cliff_context.json
include_paths=$(echo "$include_paths" | tr ',' '\n')
exclude_paths=$(echo "$exclude_paths" | tr ',' '\n')

gen_incl_excl_paths() {
	flag=${1}
	val=${2}
	retval=''
	for p in ${val}; do
		retval=$(echo -n "${retval} ${flag}=${p}")
	done

	echo ${retval}
}

gen_gha_output() {
	echo new_release_git_tag=${NEW_RELEASE_GIT_TAG}
	echo new_release_version=${NEW_RELEASE_VERSION}
	echo last_release_git_tag=${LAST_RELEASE_GIT_TAG}
	echo last_release_version=${LAST_RELEASE_VERSION}
	echo new_release_published=${NEW_RELEASE_PUBLISHED}
	cat <<-EOF
		new_release_notes<<EOT
		$(git-cliff ${cliff_args} --bump --unreleased)
		EOT
	EOF
}

# Generate git-cliff args
config_arg="--config=${config}"
tag_pattern_arg="--tag-pattern=^${tag_prefix}.+"
include_paths_arg=$(gen_incl_excl_paths '--include-path' "${include_paths}")
exclude_paths_arg=$(gen_incl_excl_paths '--exclude-path' "${exclude_paths}")
cliff_args="${config_arg} ${tag_pattern_arg} ${include_paths_arg} ${exclude_paths_arg}"

# Set GHA vars
# "git-cliff --bump --unreleased" should succeed if bump is going to happen.
# Suboptimal, since any failure of git-cliff will make the NEW_RELEASE_PUBLISHED=false
set -x
NEW_RELEASE_PUBLISHED=false
if git-cliff ${cliff_args} --bump --unreleased ; then NEW_RELEASE_PUBLISHED=true; fi
set +x

NEW_RELEASE_GIT_TAG=$(git-cliff ${cliff_args} --bump --unreleased --context | jq -r '.[0].version')
NEW_RELEASE_VERSION=${NEW_RELEASE_GIT_TAG/#${tag_prefix}/}
LAST_RELEASE_GIT_TAG=$(git-cliff ${cliff_args} --bump --unreleased --context | jq -r '.[0].previous.version')
LAST_RELEASE_VERSION=${LAST_RELEASE_GIT_TAG/#${tag_prefix}/}


gen_gha_output
if ! [ -z "${GITHUB_OUTPUT}" ]; then gen_gha_output > ${GITHUB_OUTPUT}; fi
