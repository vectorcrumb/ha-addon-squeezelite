#!/usr/bin/env python3
"""Exercise launcher input handling in a restricted, offline Podman container."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

image = sys.argv[1] if len(sys.argv) > 1 else "localhost/squeezelite-security-review:0.0.22"
engine = os.environ.get("CONTAINER_ENGINE", "podman")
# Give the container the fixture owner's UID. Rootless Podman needs keep-id;
# Docker's root without CAP_DAC_OVERRIDE cannot write a runner-owned directory.
identity_flags = ["--user", f"{os.getuid()}:{os.getgid()}"]
if Path(engine).name == "podman":
    identity_flags += ["--userns", "keep-id"]


def launch(options, expect_success=True):
    with tempfile.TemporaryDirectory(prefix="squeezelite-launcher-") as tmp:
        root = Path(tmp)
        data = root / "data"
        data.mkdir()
        (data / "options.json").write_text(json.dumps(options))
        binary = root / "capture"
        binary.write_text("#!/bin/bash\nprintf '%s\\0' \"$@\" > /data/argv\n")
        binary.chmod(0o755)
        result = subprocess.run(
            [engine, "run", "--rm", "--network", "none", "--cap-drop", "all",
             "--security-opt", "no-new-privileges", "--read-only", "--tmpfs", "/tmp",
             *identity_flags,
             "-v", f"{data}:/data:Z",
             "-v", f"{binary}:/usr/local/bin/squeezelite:ro,Z",
             "--entrypoint", "/bin/bash", image,
             "/etc/services.d/squeezelite/run"],
            capture_output=True, text=True, timeout=30,
        )
        assert (result.returncode == 0) == expect_success, result.stdout + result.stderr
        if not expect_success:
            assert not (data / "argv").exists(), "Invalid input reached the player"
            return
        args = (data / "argv").read_bytes().split(b"\0")[:-1]
        assert args[args.index(b"-s") + 1] == options["server"].encode()
        identity = args[args.index(b"-m") + 1].decode()
        if options.get("clientmac"):
            assert identity == options["clientmac"]
        else:
            import re
            assert re.fullmatch(r"02(?::[0-9a-f]{2}){5}", identity)
            assert (data / "mac").read_text().strip() == identity
            assert (data / "mac").stat().st_mode & 0o777 == 0o600
            repeated = subprocess.run(result.args, capture_output=True, text=True, timeout=30)
            assert repeated.returncode == 0, repeated.stdout + repeated.stderr
            new_args = (data / "argv").read_bytes().split(b"\0")[:-1]
            assert new_args[new_args.index(b"-m") + 1].decode() == identity
        assert (data / "name").read_text() == options["name"] + "\n"


base = {"server": "192.0.2.10:3483", "name": "Living Room", "log_level": "info",
        "clientmac": "02:00:00:00:60:01"}
launch(base)
launch({key: value for key, value in base.items() if key != "clientmac"})
# Percent escapes, shell metacharacters, and spaces must remain literal data.
launch({**base, "name": '%s %n $(id); * "quoted"'})
launch({**base, "server": "localhost;id"})
for server in ("", "-s", "localhost -S /tmp/hook", "localhost\nother"):
    launch({**base, "server": server}, expect_success=False)
launch({**base, "clientmac": "02:00:00:00:60:01 -S /tmp/hook"}, expect_success=False)
print("PASS: normal launch, literal names/arguments, invalid server and MAC rejection")
