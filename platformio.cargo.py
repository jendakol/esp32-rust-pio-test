# Cargo <-> PlatformIO integration script (autogenerated by cargo-pio)
# Calling 'pio run' will also build the Rust library crate by invoking Cargo
#
# How to use: Insert/update the following line in one of platformio.ini's environments:
# extra_scripts = platformio.cargo.py

import os

Import("projenv")

class Cargo:
    def run(self, env):
        self.__init_props(env)

        if self.__cargo_run_before_project:
            # Attach as a pre-action to all source files so that in case CBindgen is used
            # the C headers are generated before the files are compiled
            env.AddPreAction(Glob(os.path.join(env.subst("$BUILD_DIR"), "src/*.o")), self.__run_cargo)

            # Hack. Need to always run when a C file from the src directory is built, or else the include directories
            # passed to Cargo will not contain the includes coming from libraries imported with PlatformIO's Library Manager
            env.AlwaysBuild(os.path.join("$BUILD_DIR", "src/cargo.o"))

        env.AddPreAction(os.path.join("$BUILD_DIR", "$PROGNAME$PROGSUFFIX"), [self.__run_cargo, self.__link_cargo])

    def __init_props(self, env):
        self.__cargo_ran = False

        self.__rust_lib = env.GetProjectOption("rust_lib")
        self.__rust_target = env.GetProjectOption("rust_target")

        self.__rust_bindgen_enabled = env.GetProjectOption("rust_bindgen_enabled", default = "false").lower() == "true"
        self.__rust_bindgen_extra_clang_args = env.GetProjectOption("rust_bindgen_extra_clang_args", default = "")

        self.__cargo_run_before_project = env.GetProjectOption("cargo_run_before_project", default = "false").lower() == "true"
        self.__cargo_options = env.GetProjectOption("cargo_options", default = "")
        self.__cargo_profile = env.GetProjectOption(
            "cargo_profile",
            default = "release" if env.GetProjectOption("build_type") == "release" else "debug")
        self.__cargo_target_dir = env.GetProjectOption(
            "cargo_target_dir",
            default = os.path.join("$PROJECT_BUILD_DIR", "cargo")
                if env.GetProjectOption("cargo_pio_common_build_dir", default = False)
                else os.path.join("$PROJECT_DIR", "target"))

    def __run_cargo(self, source, target, env):
        if self.__cargo_ran:
            return 0

        board_mcu = env.get("BOARD_MCU")
        if not board_mcu and "BOARD" in env:
            board_mcu = env.BoardConfig().get("build.mcu")

        env["ENV"]["CARGO_PIO_BUILD_PROJECT_DIR"] = env.subst("$PROJECT_DIR")
        env["ENV"]["CARGO_PIO_BUILD_RELEASE_BUILD"] = str(env.GetProjectOption("build_type", default = "release") == "release")

        env["ENV"]["CARGO_PIO_BUILD_PATH"] = env["ENV"]["PATH"]
        env["ENV"]["CARGO_PIO_BUILD_ACTIVE"] = "1"
        env["ENV"]["CARGO_PIO_BUILD_INC_FLAGS"] = env.subst("$_CPPINCFLAGS")
        env["ENV"]["CARGO_PIO_BUILD_LIB_FLAGS"] = env.subst("$_LIBFLAGS")
        env["ENV"]["CARGO_PIO_BUILD_LIB_DIR_FLAGS"] = env.subst("$_LIBDIRFLAGS")
        env["ENV"]["CARGO_PIO_BUILD_LIBS"] = env.subst("$LIBS")
        env["ENV"]["CARGO_PIO_BUILD_LINK_FLAGS"] = env.subst("$LINKFLAGS")
        env["ENV"]["CARGO_PIO_BUILD_LINK"] = env.subst("$LINK")
        env["ENV"]["CARGO_PIO_BUILD_LINKCOM"] = env.subst("$LINKCOM")
        env["ENV"]["CARGO_PIO_BUILD_MCU"] = board_mcu

        if self.__rust_bindgen_enabled:
            env["ENV"]["CARGO_PIO_BUILD_BINDGEN_RUN"] = "True"
            env["ENV"]["CARGO_PIO_BUILD_BINDGEN_EXTRA_CLANG_ARGS"] = self.__rust_bindgen_extra_clang_args

        env["ENV"]["CARGO_PIO_BUILD_PIO_PLATFORM_DIR"] = env.PioPlatform().get_dir()[0]
        env["ENV"]["CARGO_PIO_BUILD_PIO_FRAMEWORK_DIR"] = env.PioPlatform().get_package_dir("framework-arduinoespressif32")

        self.__cargo_ran = True
        return env.Execute(f"cargo build {'--release' if self.__cargo_profile == 'release' else ''} --lib --target {self.__rust_target} {self.__cargo_options}")

    def __link_cargo(self, source, target, env):
        env.Prepend(LINKFLAGS = ["-Wl,--allow-multiple-definition"]) # A hack to workaround this issue with Rust's compiler intrinsics: https://github.com/rust-lang/compiler-builtins/issues/353
        env.Prepend(LIBPATH = [env.subst(os.path.join(self.__cargo_target_dir, self.__rust_target, self.__cargo_profile))])
        env.Prepend(LIBS = [self.__rust_lib])

# When calling into Cargo, attach to projenv instead of env, so that the (potential) SYS crates
# built by Cargo & Bindgen can also see the include directories of libraries downloaded with PlatformIO's Library Manager
# These directories are currently only passed by PlatformIO to source code __inside__ the PlatformIO project
Cargo().run(projenv)
