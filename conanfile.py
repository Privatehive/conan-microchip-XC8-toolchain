#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.files import download, copy, rmdir
from conan.errors import ConanInvalidConfiguration, ConanException
import json, os, shlex, shutil

required_conan_version = ">=2.0"


class MicrochipXC8ToolchainConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = []
    # ---Sources---
    exports = ["info.json"]
    exports_sources = ["cmake/xc8-*.cmake"]
    # ---Binary model---
    package_type = "application"
    settings = "os", "arch"
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = True

    def validate(self):
        valid_os = ["Linux"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def source(self):
        download(self, **self.conan_data["sources"][self.version], filename="xc8-installer.run")

    def _sandbox_mounts(self):
        """
        The installer insists on running as root and on creating /opt/microchip/xclm/license, regardless of --prefix.
        It also drops logs and helper scripts into /tmp. To keep the build free of root rights and side effects,
        it runs inside an unprivileged user + mount namespace with private tmpfs mounts over these locations.
        """
        own_paths = [os.path.realpath(p) for p in (self.source_folder, self.build_folder)]

        def hides_own_path(mount_point):
            return any(p == mount_point or p.startswith(mount_point + os.sep) for p in own_paths)

        # /opt/microchip is enough if it exists (a mount point must exist and can't be created without real root)
        opt = "/opt/microchip" if os.path.isdir("/opt/microchip") else "/opt"
        if hides_own_path(opt):
            raise ConanException(f"The conan build folder must not be located in {opt}")
        mounts = [opt]
        if not hides_own_path("/tmp"):
            mounts.append("/tmp")
        return mounts, opt

    def build(self):
        if not shutil.which("unshare"):
            raise ConanException("'unshare' (util-linux) is required to run the XC8 installer without root rights")

        # Copy the installer, as the source folder may be read-only and the downloaded file is not executable
        installer = os.path.join(self.build_folder, "xc8-installer.run")
        shutil.copyfile(os.path.join(self.source_folder, "xc8-installer.run"), installer)
        os.chmod(installer, 0o755)

        prefix = os.path.join(self.build_folder, "xc8")
        home = os.path.join(self.build_folder, "home")
        rmdir(self, prefix)
        rmdir(self, home)
        os.makedirs(home)

        mounts, opt = self._sandbox_mounts()
        # The installer segfaults if TMPDIR is a long path, so use a short one located on the private tmpfs
        tmpdir = os.path.join(opt, ".xc8-installer-tmp")
        install_cmd = " ".join([
            f"TMPDIR={shlex.quote(tmpdir)}",
            f"HOME={shlex.quote(home)}",
            shlex.quote(installer),
            "--mode unattended",
            "--unattendedmodeui none",
            f"--prefix {shlex.quote(prefix)}",
            "--LicenseType FreeMode",
            "--netservername localhost",
            "--ModifyAll 0",
        ])
        script = " && ".join([f"mount -t tmpfs tmpfs {m}" for m in mounts] + [f"mkdir {tmpdir}", install_cmd])
        self.output.info(f"Running the XC8 installer in a user namespace with private {' and '.join(mounts)}")
        self.run(f"unshare --user --map-root-user --mount sh -c {shlex.quote(script)}")

        if not os.path.isfile(os.path.join(prefix, "bin", "xc8-cc")):
            raise ConanException("The XC8 installer did not produce bin/xc8-cc")

    def package(self):
        prefix = os.path.join(self.build_folder, "xc8")
        copy(self, "*", src=prefix, dst=self.package_folder,
             excludes=["Uninstall*", "rollbackBackupDirectory/*"])
        copy(self, "license.txt", src=os.path.join(prefix, "docs"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "MPLAB_XC8_C_Compiler_License.rtf", src=os.path.join(prefix, "docs"),
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "xc8-*.cmake", src=os.path.join(self.source_folder, "cmake"),
             dst=os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]

        cmake_toolchain = os.path.join(self.package_folder, "cmake", "xc8-toolchain.cmake")
        self.output.info(f"Injecting cmaketoolchain:user_toolchain: {cmake_toolchain}")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", cmake_toolchain)

        self.buildenv_info.define_path("XC8_ROOT", self.package_folder)
