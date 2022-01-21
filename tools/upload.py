#!/usr/bin/env python3
import json
import os
import sys

from nexus.toolkit import Authenticator, DownloadInstance, FileManager

with open(os.path.expanduser("~/.nexus")) as f:
    config = json.load(f)

authenticator = Authenticator.from_credentials(
    username=config["username"],
    password=config["password"],
)

nexus = DownloadInstance(
    authenticator=authenticator,
    repository="ecmwf-opendata",
)

file_manager = FileManager(nexus=nexus)

file_manager.upload(
    local_path=sys.argv[1],
    remote_path=sys.argv[2],
)
