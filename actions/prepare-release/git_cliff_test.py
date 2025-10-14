import os
import pathlib

import pytest
from git_cliff import from_git_cliff_context, gen_gha_output, gen_path_args, get_by_dot, parse_tag


@pytest.mark.parametrize(
    ("d", "key", "want"),
    [
        (
            {
                "with_flow_config_processor_enrich_app": {
                    "ipport_config_values": {},
                    "ipport_config_path": "foo",
                },
            },
            "with_flow_config_processor_enrich_app.ipport_config_path",
            "foo",
        ),
    ],
)
def test_get_by_dot(d, key, want):
    assert get_by_dot(d, key) == want


@pytest.mark.parametrize(
    ("git_tag", "want"),
    [
        ("v0.1.0", "0.1.0"),
        ("v0.1.0-beta.1", "0.1.0-beta.1"),
        ("v0.1.0-rc.21", "0.1.0-rc.21"),
        ("my-awesome-app-0.10.0", "0.10.0"),
        ("my-awesome-app-0.10.0-rc.1", "0.10.0-rc.1"),
    ],
)
def test_parse_tag(git_tag, want):
    assert parse_tag(git_tag) == want


@pytest.mark.parametrize(
    ("arg", "param", "want"),
    [
        (
            "--exclude-path",
            "examples/**/*,charts/awesome-app/**/*",
            "--exclude-path=examples/**/* --exclude-path=charts/awesome-app/**/*",
        ),
        ("--include-path", "**/*", "--include-path=**/*"),
        ("--include-path", "charts/awesome-app/**/*", "--include-path=charts/awesome-app/**/*"),
    ],
)
def test_gen_path_args(arg, param, want):
    assert gen_path_args(arg, param) == want


def _load_git_cliff_context(path: str) -> str:
    prefix = pathlib.Path(os.path.realpath(__file__)).parent
    with pathlib.Path(prefix).joinpath(path).open() as fh:
        return fh.read()


@pytest.mark.parametrize(
    ("context", "key", "want"),
    [
        (
            _load_git_cliff_context("git_cliff_context_testdata.json"),
            "version",
            "v0.1.0-beta.1",
        ),
        (
            _load_git_cliff_context("git_cliff_context_testdata.json"),
            "previous.version",
            "v0.1.0-beta.0",
        ),
    ],
)
def test_from_git_cliff_context(context, key, want):
    assert from_git_cliff_context(context, key) == want


def test_gen_gha_output():
    want = (
        "new_release_published=true\n"
        "new_release_git_tag=v0.1.0-beta.1\n"
        "new_release_version=0.1.0-beta.1\n"
        "last_release_git_tag=v0.1.0-beta.0\n"
        "last_release_version=0.1.0-beta.0\n"
        "new_release_notes<<EOT\n"
        "## [v0.1.0-beta.1] - 2025-10-10\n"
        "\n"
        "### Bug Fixes\n"
        "\n"
        '- **ci:** "fetch-depth" should be 0 for releases (#143)\n'
        "### Features\n"
        "\n"
        '- **helm:** Split "awesome-app" and "awesome-app-with-os" to separate charts (#141)\n'
        "[v0.1.0-beta.0..v0.1.0-beta.1](https://github.com///compare/v0.1.0-beta.0...v0.1.0-beta.1)\n"
        "EOT"
    )

    got = gen_gha_output(
        new_release_published=True,
        new_release_git_tag="v0.1.0-beta.1",
        new_release_version="0.1.0-beta.1",
        new_release_notes=(
            "## [v0.1.0-beta.1] - 2025-10-10\n"
            "\n"
            "### Bug Fixes\n"
            "\n"
            '- **ci:** "fetch-depth" should be 0 for releases (#143)\n'
            "### Features\n"
            "\n"
            '- **helm:** Split "awesome-app" and "awesome-app-with-os" to separate charts (#141)\n'
            "[v0.1.0-beta.0..v0.1.0-beta.1](https://github.com///compare/v0.1.0-beta.0...v0.1.0-beta.1)"
        ),
        last_release_git_tag="v0.1.0-beta.0",
        last_release_version="0.1.0-beta.0",
    )
    assert got == want
