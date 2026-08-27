#!/usr/bin/env python3
"""Generate the static website release manifest from stable git tags."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

STABLE_TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def refresh_tags() -> None:
    subprocess.run(
        ["git", "fetch", "--tags", "--force", "origin"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def origin_repo_url() -> str:
    remote_url = git("remote", "get-url", "origin")
    remote_url = remote_url.removesuffix(".git")

    if remote_url.startswith("git@github.com:"):
        return f"https://github.com/{remote_url.split(':', 1)[1]}"

    return remote_url


def stable_release_tags() -> list[str]:
    refresh_tags()
    tags = git("tag", "-l").splitlines()
    parsed_tags: list[tuple[tuple[int, int, int], str]] = []

    for tag in tags:
        match = STABLE_TAG_PATTERN.fullmatch(tag.strip())
        if not match:
            continue

        version_tuple = tuple(int(part) for part in match.groups())
        parsed_tags.append((version_tuple, tag))

    parsed_tags.sort(reverse=True)
    return [tag for _, tag in parsed_tags]


def commit_date(ref: str) -> str:
    return git("log", "-1", "--format=%cs", ref).strip()


def build_manifest(base_path: str, repo_url: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    tags = stable_release_tags()

    for index, tag in enumerate(tags):
        release_root = f"{base_path}/{tag}"
        entries.append(
            {
                "version": tag,
                "name": f"{tag} (Latest Release)" if index == 0 else tag,
                "url": f"{release_root}/",
                "docsUrl": f"{release_root}/docs/",
                "releaseDate": commit_date(tag),
                "status": "latest" if index == 0 else "archived",
                "notes": f"Pinned documentation snapshot for RunZero {tag}.",
                "changelogUrl": f"{repo_url}/releases/tag/{tag}",
            }
        )

    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-path", default="/run-zero")
    parser.add_argument("--repo-url", default=origin_repo_url())
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(build_manifest(args.base_path.rstrip("/"), args.repo_url.rstrip("/")), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
