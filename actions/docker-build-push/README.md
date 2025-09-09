# Overview

A composite action to build/push docker images to arbitrary registries, supports Github Action caching (optional)

## Examples

### Github Container Registry (ghcr.io)

CI:

```yaml
  docker_build:
    name: Docker build
    runs-on: ${{ matrix.runner }}
    timeout-minutes: 30
    strategy:
      matrix:
        runner: [ubuntu-latest, ubuntu-latest-arm]
        target: [runner, runner-debug]
    env:
      RUNNER_PLATFORM: |
        {
            "ubuntu-latest": "linux/amd64",
            "ubuntu-latest-arm": "linux/arm64"
        }
    steps:
      - name: Checkout
        uses: actions/checkout@v5
      - name: Build docker image
        uses: ./.github/actions/docker-build-push
        with:
          platforms: ${{ fromJson(env.RUNNER_PLATFORM)[matrix.runner] }}
          target: ${{ matrix.target }}
          cache_from: 'type=gha'
          cache_to: ${{ github.ref_name == 'main' && 'type=gha,mode=max' || '' }}
```

Release:

```yaml
  docker_build_push:
    name: Docker build/push
    runs-on: ${{ matrix.runner }}
    timeout-minutes: 30
    permissions:
      contents: read
      packages: write
      attestations: write
      id-token: write
    strategy:
      matrix:
        runner: [ubuntu-latest, ubuntu-latest-arm]
        target: [runner, runner-debug]
    env:
      RUNNER_PLATFORM: |
        {
            "ubuntu-latest": "linux/amd64",
            "ubuntu-latest-arm": "linux/arm64"
        }
      TARGET_IMAGE_TAG: |
        {
            "runner": "v0.1.0.rc",
            "runner-debug": "v0.1.0.rc-debug"
        }
    steps:
      - name: Checkout
        uses: actions/checkout@v5
      - name: Build docker image
        uses: ./.github/actions/docker-build-push
        with:
          registry: ghcr.io
          image: ${{ github.repository }}
          tag: ${{ fromJson(env.TARGET_IMAGE_TAG)[matrix.target] }}
          platforms: ${{ fromJson(env.RUNNER_PLATFORM)[matrix.runner] }}
          target: ${{ matrix.target }}
          push: true
          cache_from: 'type=gha'
          cache_to: ${{ github.ref_name == 'main' && 'type=gha,mode=max' || '' }}
          registry_username: ${{ github.actor }}
          registry_password: ${{ secrets.GITHUB_TOKEN }}
```
