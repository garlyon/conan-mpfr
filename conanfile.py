from conans import ConanFile, tools, AutoToolsBuildEnvironment
from pathlib import Path


class MpfrConan(ConanFile):
    name = "mpfr"
    version = "4.0.1"
    license = "LGPL v3"
    url = "git@github.com:garlyon/conan-mpfr.git"
    description = "The MPFR library is a C library for multiple-precision floating-point computations with correct rounding"
    settings = "os", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    no_copy_source = True
    requires = "gmp/[>=5.0]@grif/dev"

    def source(self):
        tools.get("https://www.mpfr.org/mpfr-current/{}.tar.bz2".format(self.full_name))

    def imports(self):
        # allow configure' tests find gmp dll
        self.copy("*.dll", src="bin")

    def build(self):
        # issue https://github.com/conan-io/conan/issues/2982
        with tools.environment_append(self.wsl_env):
            build_env = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            build_env.configure(
                configure_dir=self.configure_dir,
                host=self.host,
                args=self.configure_args,
                vars=self.configure_envs)
            build_env.make()
            build_env.install()
        # Create import library for implicit linkage with dll
        if self.settings.os == "Windows" and self.options.shared:
            self.make_dll_import_lib()

    def package(self):
        # performed by install step
        pass

    def package_info(self):
        self.cpp_info.libs = ["mpfr"]
        # gcc doesn't support SEH for x86
        if self.settings.os == "Windows" and self.settings.arch == "x86":
            self.cpp_info.sharedlinkflags = ["/SAFESEH:NO"]
            self.cpp_info.exelinkflags = ["/SAFESEH:NO"]
    
    @property
    def full_name(self):
        return "{}-{}".format(self.name, self.version)

    @property
    def host(self):
        return tools.get_gnu_triplet(self.settings.os.value, self.settings.arch.value, "gcc")

    @property
    def configure_dir(self):
        # location of autoconf script
        return str(Path(self.source_folder).joinpath(self.full_name))

    @property
    def configure_args(self):
        args = []
        # override prefix from AutoToolsBuildEnvironment with correct path format
        args.append("--prefix={}".format(tools.unix_path(self.package_folder)))
        if self.options.shared:
            args.extend(["--enable-shared", "--disable-static"])
        else:
            args.extend(["--enable-static", "--disable-shared"])
        args.append("--with-pic")
        args.append("--with-gmp={}".format(tools.unix_path(self.gmp_root)))
        return args

    @property
    def configure_envs(self):
        envs = {}
        if tools.os_info.is_windows:
            # enforce static linkage with libgcc
            envs["CC"] = "{}-gcc -static-libgcc".format(self.host)
        return envs

    @property
    def gmp_root(self):
        return self.deps_cpp_info["gmp"].rootpath

    @property
    def wsl_env(self):
        # list of influential environment variables from mpfr config help
        env_vars_to_forward = [
            "CC/u",
            "CFLAGS/u",
            "LDFLAGS/u",
            "LIBS/u",
            "CPPFLAGS/u",
            "CPP/u",
            "LT_SYS_LIBRARY_PATH/u"]
        return {"WSLENV": ":".join(env_vars_to_forward)}

    def make_dll_import_lib(self):
        # create dll import lib directly in package folder
        lib_file = Path(self.package_folder).joinpath("lib", "mpfr.lib")
        # use dlltool to make import lib from def file
        command = "{host}-dlltool -d {def_file} -D {dll_name} -l {lib_file}".format(
            host=self.host,
            def_file="src/.libs/libmpfr-6.dll.def",
            dll_name="libmpfr-6.dll",
            lib_file=tools.unix_path(str(lib_file)))
        # execute in bash
        self.run(command, win_bash=tools.os_info.is_windows)
