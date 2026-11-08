# conan-microchip-XC8-toolchain

[![Conan Remote Recipe](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FPrivatehive%2Fconan-microchip-XC8-toolchain%2Fproperties%2Fvalues&query=%24%5B0%5D.value&style=flat&logo=conan&label=conan&color=%232980b9)](https://conan.privatehive.de/ui/repos/tree/General/public-conan/de.privatehive/microchip-xc8-toolchain)

#### A conan package for the Microchip MPLAB XC8 C compiler (PIC).

---

| os      | arch     | CI Status                                                                                                                                                                                                                                                                                                   |
| ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Linux` | `x86_64` | [![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Privatehive/conan-microchip-XC8-toolchain/main.yml?branch=master&style=flat&logo=github&label=create+package)](https://github.com/Privatehive/conan-microchip-XC8-toolchain/actions?query=branch%3Amaster) |

Only the recipe is uploaded to the conan remote, not the binary package (see [License](#license)).
`conan create`/`conan install` with `-b missing` builds the package locally from Microchip's installer.

The package is built from Microchip's official installer
(`xc8-v3.10-full-install-linux-x64-installer.run`, see [conandata.yml](conandata.yml)).
It needs neither root rights nor any additional system packages.

## Create the package

```shell
conan create .
```

The installer insists on running as root and writes to `/opt/microchip/xclm` and `/tmp` regardless of `--prefix`.
That's why the recipe runs it unattended inside an unprivileged user + mount namespace
(`unshare --user --map-root-user --mount`, part of util-linux) with private tmpfs mounts over those locations.
Nothing is written outside the conan cache. The build host must allow unprivileged user namespaces.
That's the default on most distributions, but Ubuntu 24.04 restricts them via AppArmor.

## Usage

The package injects a CMake toolchain file via `tools.cmake.cmaketoolchain:user_toolchain` and puts the XC8 binaries on the `PATH`.
The usual way to use it is a host profile:

```ini
[settings]
os=baremetal
build_type=Debug

[tool_requires]
microchip-xc8-toolchain/3.10@de.privatehive/stable
```

Conan has no PIC architecture, so leave `arch` and `compiler` unset (and don't declare them in the consuming recipe).

The toolchain file requires two CMake variables:

| Variable  | Description                                                                                                        |
| --------- | ------------------------------------------------------------------------------------------------------------------ |
| `XC8_MCU` | Target device as accepted by `-mcpu`, e.g. `16LF1509`. Usually set in `CMakeLists.txt` **before** `project()`.     |
| `XC8_DFP` | Path to the `xc8` folder of an unpacked Device Family Pack (DFP). Usually passed by the consuming recipe.          |

Since XC8 v3.00 the compiler ships **no device support** of its own, so a DFP is always required.
DFPs (`.atpack`, a zip archive) can be downloaded from https://packs.download.microchip.com/.
A consuming recipe can fetch one in `source()` (only the `xc8/` folder is needed) and hand it to CMake:

```python
def source(self):
    get(self, url="https://packs.download.microchip.com/Microchip.PIC12-16F1xxx_DFP.1.8.254.atpack",
        sha256="6af7b37fa586910cf821bcbec258470b1e3a3fe4ddb9355ce1405cc6e4c93698", destination="dfp", pattern="xc8/*")

def generate(self):
    tc = CMakeToolchain(self, generator="Ninja")
    tc.cache_variables["XC8_DFP"] = os.path.join(self.source_folder, "dfp", "xc8")
    tc.generate()
```

`CMAKE_BUILD_TYPE` maps to the following flags. The unlicensed (Free) compiler supports up to `-O2`.

| Build type       | Flags             |
| ---------------- | ----------------- |
| `Debug`          | `-O0 -gdwarf-3`   |
| `Release`        | `-O2`             |
| `RelWithDebInfo` | `-O2 -gdwarf-3`   |
| `MinSizeRel`     | `-O2`             |

Example project: [ThePerfectCounter](https://github.com/Tereius/ThePerfectCounter)

## License

The compiler is installed in Free mode and is subject to the
[MPLAB XC8 C Compiler License](https://www.microchip.com/en-us/tools-resources/develop/mplab-xc-compilers), which is packaged in `licenses/`.
Don't upload the binary package to a public remote, as that redistributes the compiler.
