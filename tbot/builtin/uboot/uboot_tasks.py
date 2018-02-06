"""
Collection of U-Boot tasks
--------------------------
"""
import os
import tbot

@tbot.testcase
def check_uboot_version(tb, uboot_bin="{builddir}/u-boot.bin"):
    """
    Check whether the version of U-Boot running on the board is the same
    as the one supplied as a binary file in uboot_bin.

    :param uboot_bin: Path to the U-Boot binary. "{builddir}" will be replaced
                      with the U-Boot build dir used by tbot. (str)
    :returns: Nothing
    """
    with tb.with_boardshell() as tbn:
        filename = uboot_bin.format(builddir=os.path.join(
            tb.config.workdir,
            f"u-boot-{tb.config.board_name}"))
        strings = tbn.shell.exec0(f"strings {filename} | grep U-Boot", log_show=False)
        version = tbn.boardshell.exec0("version").split('\n')[0]
        assert version in strings, "U-Boot version does not seem to match"
