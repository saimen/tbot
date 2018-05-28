import tbot


@tbot.testcase
def selftest_buildhost(tb: tbot.TBot) -> None:
    with tb.machine(tbot.machine.MachineBuild()) as tb:
        tb.buildshell.exec0("uname -a")
        toolchain = tb.call("toolchain_get")

        @tb.call_then("toolchain_env", toolchain=toolchain)
        def build(tb: tbot.TBot) -> None:
            tb.buildshell.exec0("echo $CC")
