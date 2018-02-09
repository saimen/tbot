from tbot.config import Config

#pylint: disable=line-too-long
def config(cfg: Config) -> None:
    def validate(cfg: Config):
        if cfg["lab.name"] != "pollux":
            raise Exception("board taurus: Only availabe in pollux lab!")
    cfg["_marker.taurus"] = validate

    cfg["board"] = {
        "name": "at91_taurus",
        "toolchain": "generic-armv7a-hf",
        "defconfig": "taurus_defconfig",
    }

    cfg["uboot"] = {
        "patchdir": "/work/hs/tbot/patches/taurus_uboot_patches",
        "env_location": "/home/hws/env/taurus-env.txt",
    }

    cfg["tftp"] = {
        "boarddir": "at91_taurus",
    }
