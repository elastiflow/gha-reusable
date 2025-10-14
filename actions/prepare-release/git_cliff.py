import argparse
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", help="Makefile to run", required=True)
    parser.add_argument("--tag-prefix", dest="tag_prefix", help="git-cliff tag prefix", required=True)
    parser.add_argument("--include-paths", dest="include_paths", help="List of git-cliff --include-path", required=True)
    parser.add_argument("--exclude-paths", dest="exclude_paths", help="List of git-cliff --exclude-path", required=True)
    return parser.parse_args()


def get_by_dot(d: dict, key: str) -> str:
    if "." in key:
        key, rest = key.split(".", 1)
        return get_by_dot(d[key], rest)

    return str(d[key])


def parse_tag(git_tag: str) -> str:
    """Strip prefix from a semver tag and output only version."""
    # https://regex101.com/r/NisV7D/4
    return re.sub(
        r"(?:[a-z]|-)+?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:-(?:rc|alpha|beta)\.?(?:(?:[0-9]{1,3}\.?)?)+)?)",
        r"\1",
        git_tag,
    )


def gen_path_args(arg: str, param: str) -> str:
    if not param or not param.strip():
        return ""
    return " ".join([f"{arg}={p}" for p in param.split(",") if p.strip()])


def run_git_cliff(args: str, exit_failure: bool = True) -> subprocess.CompletedProcess[str]:  # noqa: FBT001,FBT002
    c = shlex.split(f"git-cliff {args}")
    res = subprocess.run(c, capture_output=True, text=True, check=False)  # noqa: S603
    if res.returncode != 0 and exit_failure:
        print(f"Error running command: git-cliff {args}")  # noqa: T201
        print(f"stdout: {res.stdout}")  # noqa: T201
        print(f"stderr: {res.stderr}")  # noqa: T201
        sys.exit(1)
    return res


def from_git_cliff_context(context: str, key: str) -> str:
    c = json.loads(context)
    return get_by_dot(c[0], key)


def gen_gha_output(  # noqa: PLR0913
    new_release_published,  # noqa: ANN001
    new_release_git_tag,  # noqa: ANN001
    new_release_version,  # noqa: ANN001
    new_release_notes,  # noqa: ANN001
    last_release_git_tag,  # noqa: ANN001
    last_release_version,  # noqa: ANN001
) -> str:
    changelog = f"new_release_notes<<EOT\n{new_release_notes}\nEOT"

    out = [
        f"new_release_published={json.dumps(new_release_published)}",
        f"new_release_git_tag={new_release_git_tag}",
        f"new_release_version={new_release_version}",
        f"last_release_git_tag={last_release_git_tag}",
        f"last_release_version={last_release_version}",
        changelog,
    ]
    return "\n".join(out)


if __name__ == "__main__":
    args = parse_args()

    cliff_config_arg = f"--config={args.config}"
    cliff_tag_pattern_arg = f"--tag-pattern=^{args.tag_prefix}.+"
    cliff_include_path_arg = gen_path_args("--include-path", args.include_paths)
    cliff_exclude_path_arg = gen_path_args("--exclude-path", args.exclude_paths)
    cliff_args = f"{cliff_config_arg} {cliff_tag_pattern_arg} {cliff_include_path_arg} {cliff_exclude_path_arg}"

    # Fill the outputs
    new_release_published = run_git_cliff(f"{cliff_args} --bump --unreleased", exit_failure=False).returncode == 0
    new_release_git_tag = from_git_cliff_context(
        run_git_cliff(f"{cliff_args} --bump --unreleased --context").stdout,
        "version",
    )
    new_release_version = parse_tag(new_release_git_tag)
    new_release_notes = run_git_cliff(f"{cliff_args} --bump --unreleased").stdout
    last_release_git_tag = from_git_cliff_context(
        run_git_cliff(f"{cliff_args} --bump --unreleased --context").stdout,
        "previous.version",
    )
    last_release_version = parse_tag(last_release_git_tag)

    if new_release_published:
        out = gen_gha_output(
            new_release_published=new_release_published,
            new_release_git_tag=new_release_git_tag,
            new_release_version=new_release_version,
            new_release_notes=new_release_notes,
            last_release_git_tag=last_release_git_tag,
            last_release_version=last_release_version,
        )
    else:
        out = gen_gha_output(
            new_release_published=False,
            new_release_git_tag="",
            new_release_version="",
            new_release_notes="",
            last_release_git_tag="",
            last_release_version="",
        )

    print(out)  # noqa: T201
    if os.getenv("GITHUB_OUTPUT"):
        with pathlib.Path(str(os.getenv("GITHUB_OUTPUT"))).open("w+") as fh:
            fh.write(out)
