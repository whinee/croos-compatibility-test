import base64
import hashlib
import json
import multiprocessing.dummy as mp
import os
import shlex
import shutil
import stat
import subprocess
from collections.abc import Callable, Collection
from io import BytesIO
from sys import platform as PLATFORM
from typing import Any, Optional, Union

from PIL import Image, ImageOps

from validate import validate_mermaid_config

# Types
CONFIG_TYPE = bool | int | str | dict[str, Union[bool, int, str, "CONFIG_TYPE"]]
MMD_LS_TYPE = list[dict[str, str | Collection[str] | CONFIG_TYPE]]

# Constants

## Program Constants
RESULTS_MD_TPL = """# Results

| Index | Checksum                         | Expected Checksum                | Matching? |
|:-----:|:--------------------------------:|:--------------------------------:|:---------:|
{}

{}
"""

match PLATFORM:
    case "win32":
        OS = "Windows"
        file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "mermaid-electron.exe",
        )
        os.chmod(file_name, os.stat(file_name).st_mode | stat.S_IXUSR)
        CMD = file_name.replace("\\", "\\\\")
        # CMD = "powershell -Command " + file_name.replace("\\", "\\\\")

    case "darwin":
        OS = "MacOS"
        mount_output = (
            subprocess.check_output(
                shlex.split(  # noqa: S603
                    "hdiutil attach -nobrowse mermaid-electron.dmg",
                ),
            )
            .decode()
            .strip()
        )
        volume_name = (
            subprocess.check_output(
                shlex.split('echo "' + mount_output + '"'),  # noqa: S603
            )
            .decode()
            .strip()
            .split("/Volumes/", 1)[1]
        )

        volume_path = os.path.join("/Volumes", volume_name)

        CMD = "mermaid-electron.app"

        shutil.copytree(
            os.path.join(volume_path, "mermaid-electron.app"),
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "mermaid-electron.app",
            ),
        )

        # Set the executable permissions on the copied application
        CMD = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "mermaid-electron.app",
            "Contents",
            "MacOS",
            "mermaid-electron",
        )
        os.chmod(CMD, os.stat(CMD).st_mode | stat.S_IXUSR)

    case "linux":
        OS = "Linux"
        CMD = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "mermaid-electron.AppImage",
        )

IMG_FN_TPL = "screenshot-{}.png"
IMG_TPL = f"![](https://github.com/whinee/cross-compatibility-test/releases/download/{OS}/{IMG_FN_TPL})"

print(CMD)


def calculate_checksum(data: str) -> str:
    return hashlib.md5(data.encode()).hexdigest()  # noqa: S324


def b64_2_image(vdata: dict[str, Any]) -> Callable[..., None]:
    margin = vdata["config"]["margin"]

    margin2 = margin * 2

    def inner(idx: int, img_b64: str) -> None:
        # Decode base64 and open image in Pillow
        img = Image.open(BytesIO(base64.b64decode(img_b64)))

        # Get inverted grayscale copy of the image
        img_gray = img.convert("L")
        img_inv = ImageOps.invert(img_gray)

        # Then get the bounding box of the non-zero region in the image
        bbox = img_inv.getbbox()

        # And afterwards crop the image using the bounding box tuple
        cropped_img = img.crop(bbox)

        # If the margin is not set, then do not apply one, and just save it
        if not margin:
            cropped_img.save(f"screenshot-{idx}.png")
            return

        # Otherwise, make a new image `2 * margin` larger than the size of the
        # original screenshot
        bordered_img = Image.new(
            "RGB",
            (cropped_img.width + margin2, cropped_img.height + margin2),
            color="white",
        )

        # Then paste the image in the center, and afterwards save the image
        bordered_img.paste(cropped_img, (margin, margin))
        bordered_img.save(f"screenshot-{idx}.png")

    return inner


def run_mermaid_electron(cmd: str, data: dict[str, Any]) -> None:
    cs_ls = []
    results = []

    expected_cs_ls = [i.pop("checksum") for i in data["mmd"]]

    vdata = validate_mermaid_config(data)

    img_fn = b64_2_image(vdata)
    data_str = json.dumps(vdata)

    process = subprocess.Popen(
        shlex.split(cmd),  # noqa: S603
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = process.communicate(data_str)

    if stderr:
        raise Exception(stderr)

    print(type(stdout))
    print(stdout)

    img_ls: list[str] = json.loads(stdout)

    p = mp.Pool(10)
    p.starmap(img_fn, enumerate(img_ls))
    p.close()
    p.join()

    for expected, (idx, img_b64) in zip(expected_cs_ls, enumerate(img_ls), strict=True):
        matching: Optional[bool] = None

        r_cs: str = calculate_checksum(img_b64)

        cs_ls.append(r_cs)

        if expected:
            matching = r_cs == expected
            print(idx, matching)
        else:
            expected = ""

        results.append(
            [
                "{: <5}".format(str(idx)),
                "{: <32}".format(str(r_cs)),
                "{: <32}".format(str(expected)),
                "{: <9}".format(str("N/A" if matching is None else matching)),
            ],
        )

    results_md = RESULTS_MD_TPL.format(
        "\n".join(["| " + " | ".join([str(j) for j in i]) + " |" for i in results]),
        "\n".join([IMG_TPL.format(i) for i in range(0, len(img_ls))]),
    )

    with open("results.md", "w") as f:
        f.write(results_md)

    with open("to-be-uploaded.txt", "w") as f:
        f.write("\n".join([IMG_FN_TPL.format(i) for i in range(0, len(img_ls))]))


mmd_ls = [
    {
        "code": """gantt
    title A Gantt Diagram
    dateFormat YYYY-MM-DD
    section Section
    A task :a1, 2014-01-01, 30d
    Another task :after a1 , 20d
    section Another
    Task in sec :2014-01-12 , 12d
    another task : 24d
""",
        "config": {"theme": "forest"},
        "checksum": "010f8556485aa9778bb1a9b465f7057a",
    },
    {
        "code": """flowchart TD
        intro --> tt
    """,
        "config": {"theme": "forest"},
        "checksum": "182815483826ffac4d2044d8db2de019",
    },
    {
        "code": """flowchart TD
        intro --> tt
    """,
        "checksum": "dd21cf872491bfe2003e5c53997dfed1",
    },
]

data = {
    "mmd": mmd_ls,
    "mmd_config": {
        "theme": "dark",
    },
    "config": {
        "width": 1200,
        "zoom": 1.5,
    },
}


run_mermaid_electron(CMD, data)
