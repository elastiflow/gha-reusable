# Overview

`prepare-release` is the opinionated way to generate [semver](https://semver.org/) version number and changelog using [git-cliff](https://git-cliff.org/docs/).  
Action supports:

- Generate and update the Changelog
- Update version in the arbitrary YAML manifest

Note, the action will not perform any releases or pushes, used purely to:

- Determine if release should happen
- Generate next version number
- Generate changelog

It is expected this action to be used with other actions to perform tag and release, for example to create a "release" PR:

```yaml
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout
        uses: actions/checkout@v5
        with:
          fetch-depth: 0 # Required, git-cliff uses the local git repo to read through tags and commits
      - name: Prepare Release
        id: prepare_release
        uses: elastiflow/gha-reusable/actions/prepare-release@v0
        with:
          add_git_notes: true
          changelog_update: true
          bump_version_yaml: true
          bump_version_yaml_path: galaxy.yml
          bump_version_yaml_key: '.version'
      - name: Create and push semver tag
        if: ${{ fromJson(steps.prepare_release.outputs.new_release_published) }}
        uses: anothrNick/github-tag-action@e528bc2b9628971ce0e6f823f3052d1dcd9d512c
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CUSTOM_TAG: v${{ steps.prepare_release.outputs.new_release_version }}
      - name: Create GH release
        if: ${{ fromJson(steps.prepare_release.outputs.new_release_published) }}
        uses: softprops/action-gh-release@72f2c25fcb47643c292f7107632f7a47c1df5cd8
        with:
          tag_name: v${{ steps.prepare_release.outputs.new_release_version }}
          body: ${{ steps.prepare_release.outputs.new_release_notes }}
          target_commitish: ${{ github.ref_name }}
          preserve_order: true
          make_latest: true
```

Please see the action manifest `inputs`/`outputs` for the config details.

## Monorepo support (experimental)

This action may be used with monorepos, provided the directory structure is properly configured. `include_paths` and `exclude_paths` options are used to determine commits related to a release.
Additionally it's a good idea to define `tag_prefix` to be `appname-` to so the action only counts `appname-` prefixed tags.
