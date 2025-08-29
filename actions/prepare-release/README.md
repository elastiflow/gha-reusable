# Overview

`prepare-release` is the opinionated way to generate [semver](https://semver.org/) version number using [semantic-release](https://github.com/semantic-release/semantic-release).  
Action supports:

- Generate and update the Changelog
- Update version in the arbitrary YAML manifest
- Optionally (default `false`) commit and push changes back to the branch.

Note, `semantic-release` will not perform any release, used purely to:

- Generate next version number
- Generate changelog

It is expected this action to be used with other actions to perform tag and release, for example:

```yaml
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout
        uses: actions/checkout@v5
      - name: Prepare Release
        id: prepare_release
        uses: ./.github/actions/composite_release
        with:
          branch: "${{ github.ref_name }}"
          changelog_update: true
          bump_version_yaml: true
          bump_version_yaml_path: galaxy.yml
          bump_version_yaml_key: '.version'
          github_token: ${{ secrets.GITHUB_TOKEN }}
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
          preserve_order: true
          make_latest: true
```

Please see the action manifest `inputs`/`outputs` for the config details.
