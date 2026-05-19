# update-gitops

Composite GitHub Action that syncs manifest files into a GitOps branch and bumps a version key in YAML files.

## What it does

1. Detects (or accepts) the default branch.
2. Checks out the GitOps branch.
3. Copies the specified manifest file(s) from the default branch into the GitOps branch.
4. Updates a version key in one or more YAML files using the short commit SHA.
5. Commits and optionally pushes the changes.
6. Adds the GHA status with new commit and diff

## Usage

```yaml
- name: Update GitOps
  uses: elastiflow/gha-reusable/actions/update-gitops@v0
  with:
    manifests_path: deploy/foobar/k8s,deploy/foobar/config.hcl
    bump_version_yaml_path: deploy/foobar/k8s/values.yaml
    bump_version_yaml_key: .image.tag
    github_token: "${{ secrets.GITHUB_TOKEN }}"
```

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `manifests_path` | yes | — | Comma-separated paths to manifest files to sync from the default branch |
| `gitops_branch` | no | `gitops` | Target GitOps branch |
| `default_branch` | no | `""` | Source branch to sync from |
| `docker_tag_prefix` | no | `commit_` | Prefix prepended to the commit SHA when writing the image tag |
| `bump_version_yaml_path` | yes | — | Comma-separated paths to YAML files to update |
| `bump_version_yaml_key` | yes | — | [yq](https://mikefarah.gitbook.io/yq)-style key path to update |
| `git_config_email` | no | `devops@elastiflow.com` | Git config email |
| `git_config_user_name` | no | `DevOps Elastiflow` | Git config user name |
| `push` | no | `false` | Set `"true"` to commit and push changes to the GitOps branch |
| `github_token` | no | — | Token with write access; required when `push` is `true` |

## Outputs

| Output | Description |
| --- | --- |
| `new_commit_sha` | Short SHA of the default branch commit used for the update |

## Requirements

- [`yq`](https://mikefarah.gitbook.io/yq) must be available on the runner.
