import argparse
import re
from pathlib import Path

import yaml

from . import INTAKES_PATH, Validator
from .constants import CheckResult


class ManifestValidator(Validator):
    """
    Check the module/format has a proper manifest
    """

    @classmethod
    def validate(cls, result: CheckResult, args: argparse.Namespace) -> None:
        if not result.options.get("meta_dir"):
            return

        module_meta_dir: Path = result.options["meta_dir"]
        module_manifest_file = module_meta_dir / "manifest.yml"

        check_manifest(manifest_file_path=module_manifest_file, result=result, args=args)


def check_manifest(manifest_file_path: Path, result: CheckResult, args: argparse.Namespace) -> None:
    if not manifest_file_path.is_file():
        result.errors.append(f"manifest file (`{manifest_file_path.relative_to(INTAKES_PATH)}`) is missing")
        return

    # check the format/module has a valid manifest
    try:
        with open(manifest_file_path, "r") as fd:
            manifest_content = yaml.safe_load(fd)

    except Exception as any_error:
        result.errors.append(f"manifest file cannot be loaded (`{any_error}`)")
        return

    result.options["manifest_file_path"] = manifest_file_path

    # check the format/module has a uuid
    manifest_uuid = manifest_content.get("uuid")
    if not manifest_uuid:
        result.errors.append("no uuid found in the manifest file")

    else:
        result.options["manifest_uuid"] = manifest_uuid

    # check the format/module has a name
    manifest_name = manifest_content.get("name")
    if not manifest_name:
        result.errors.append("no name found in the manifest file")

    else:
        result.options["manifest_name"] = manifest_name

    # check the format/module has a slug
    manifest_slug = manifest_content.get("slug")
    if not manifest_slug:
        result.errors.append("no slug found in the manifest file")

    elif not re.match(r"^[a-z]([a-z]|-|\d)*$", manifest_slug):
        result.errors.append("incorrect slug in the manifest file")

    else:
        result.options["manifest_slug"] = manifest_slug

    # check the format/module has a description
    if "description" not in manifest_content:
        result.errors.append("no description found in the manifest file")

    elif not args.ignore_empty_descriptions and len(manifest_content.get("description")) == 0:
        result.errors.append("description is found, but empty")
