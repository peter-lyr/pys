import os
import re
import shutil
import sys


def rep(text):
    return text.replace("\\", "/").lower()


def rm_build_dirs(project_root):
    rms = ["build", ".cache"]
    for root, dirs, _ in os.walk(project_root):
        for r in rms:
            if r in dirs:
                r = rep(os.path.join(root, r))
                if os.path.exists(r):
                    try:
                        print(f"Deleting {r}, ", end="")
                        shutil.rmtree(r)
                        print(f"Deleted {r}.")
                    except:
                        pass


def get_libs_a_dirs(project_root):
    lib_a_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".a"):
                dir = os.path.dirname(
                    rep(os.path.join(root, file))
                    .replace("\\", "/")
                    .replace(project_root, "")
                    .strip("/")
                )
                if dir not in lib_a_files:
                    lib_a_files.append(dir)
    return lib_a_files


def get_executable_cbp(project_root):
    cbp_files = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".cbp"):
                cbp_files.append(rep(os.path.join(root, file)))
    executable_cbp = ""
    temp_app_cbps = []
    if len(cbp_files) == 1:
        executable_cbp = cbp_files[0]
    elif len(cbp_files) > 1:
        for cbp_file in cbp_files:
            if os.path.basename(cbp_file) in ["app.cbp"]:
                temp_app_cbps.append(cbp_file)
        else:
            if not temp_app_cbps:
                temp_app_cbps = cbp_files
        if len(temp_app_cbps) == 1:
            executable_cbp = temp_app_cbps[0]
        else:
            res = input(
                "Type number to choose one of cbp as executable\n"
                + "\n".join(
                    [str(i + 1) + ". " + v for i, v in enumerate(temp_app_cbps)]
                )
                + "\n"
                ">> "
            )
            try:
                num = int(res)
                if num in [i + 1 for i, _ in enumerate(cbp_files)]:
                    executable_cbp = cbp_files[num - 1]
            except Exception as e:
                print(e)
    cbp_files_2 = []
    for cbp_file in cbp_files:
        if cbp_file not in temp_app_cbps:
            cbp_files_2.append(cbp_file)
    return executable_cbp, cbp_files_2


def get_files_and_dirs(project_root, executable_cbp, executable_cbp_dir):
    patt1 = re.compile('directory="(.+)"')
    patt2 = re.compile('filename="(.+?[cSp])"')
    with open(executable_cbp, "rb") as fff:
        content = fff.read().decode("utf-8")
    directories = []
    files = []
    for directory in re.findall(patt1, content):
        directory = (
            os.path.normpath(os.path.join(executable_cbp_dir, directory))
            .replace("\\", "/")
            .replace(project_root, "")
            .strip("/")
        )
        if directory not in directories and os.path.exists(directory):
            directories.append(directory)
    for file in re.findall(patt2, content):
        file = (
            os.path.normpath(os.path.join(executable_cbp_dir, file))
            .replace("\\", "/")
            .replace(project_root, "")
            .strip("/")
        )
        if file not in files and os.path.exists(file):
            files.append(file)
    return files, directories


def is_test_dir(f):
    l = f.split("/")
    for _f in l:
        if not _f:
            return 0
        if _f[0] == ".":
            return 1
        for _I in ["test", "bak", "build", ".cache"]:
            if _I in _f:
                return 1
    return 0


def check(project_root):
    I = []
    res = os.popen("git ls-files --exclude-standard --ignored --others").read()
    for line in res.splitlines():
        I.append(rep(line))

    D = [""]
    F = []
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.split(".")[-1] in ["c", "h", "cpp"]:
                f = (
                    rep(os.path.join(root, file))
                    .replace(project_root + "/", "")
                    .strip("/")
                )
                if f in I:
                    continue
                if is_test_dir(f):
                    continue
                if file.split(".")[-1] in ["c", "cpp"]:
                    F.append(f)
                d = rep(root).replace(project_root, "").strip("/")
                if not is_test_dir(d):
                    d = d.lstrip("/")
                    if d not in D:
                        D.append(d)
    return D, F


if __name__ == "__main__":
    if len(sys.argv) < 2:
        os._exit(1)

    project_root = rep(sys.argv[1])
    print("project_root:", project_root)
    os.chdir(project_root)

    rm_build_dirs(project_root)

    executable_cbp, cbp_files = get_executable_cbp(project_root)
    executable_cbp_dir = os.path.dirname(executable_cbp)
    print("executable_cbp_dir:", executable_cbp_dir)

    if executable_cbp:
        executable_files, executable_dirs = get_files_and_dirs(
            project_root, executable_cbp, executable_cbp_dir
        )
        print("project_root:", project_root)
        print(len(executable_files), "files,", len(executable_dirs), "dirs")
        print("executable_cbp:", executable_cbp)
        with open(os.path.join(project_root, "CMakeLists.txt"), "wb") as ff:
            ff.write(b"cmake_minimum_required(VERSION 3.5)\n")
            ff.write(b"set(PROJECT_NAME proj_name)\n")
            ff.write(b"project(${PROJECT_NAME})\n\n")

            # executable_cbp
            ff.write(b"add_executable(${PROJECT_NAME}\n")
            for f in executable_files:
                f = '        "${PROJECT_SOURCE_DIR}/' + f + '"\n'
                ff.write(f.encode("utf-8"))
            ff.write(b"        )\n")
            ff.write(b"target_include_directories(${PROJECT_NAME} PUBLIC\n")
            for d in executable_dirs:
                d = (
                    d.replace("\\", "/")
                    .replace(project_root, "")
                    .strip("\\")
                    .strip("/")
                    .replace("\\", "/")
                )
                d = '              "${PROJECT_SOURCE_DIR}/' + d + '"\n'
                ff.write(d.encode("utf-8"))
            ff.write(b"              )\n")

            # lib_cbp
            lib_cbp_files = {}
            for lib_cbp_file in cbp_files:
                if lib_cbp_file == executable_cbp:
                    continue
                base_name = os.path.basename(lib_cbp_file)
                if base_name not in lib_cbp_files.keys():
                    lib_cbp_files[base_name] = [lib_cbp_file]
                else:
                    lib_cbp_files[base_name].append(lib_cbp_file)

            lib_cbp_files_list = []

            for base_name, lib_cbp_files in lib_cbp_files.items():
                lib_cbp_file = lib_cbp_files[0]
                if len(lib_cbp_files) > 1:
                    l = len(lib_cbp_files)
                    print("sel as " + base_name + ":")
                    for i in range(l):
                        print(str(i + 1) + ". " + lib_cbp_files[i])
                    idx = input("> ")
                    try:
                        idx = int(idx)
                        if idx < 1:
                            idx = 1
                        elif idx > l:
                            idx = l
                        idx -= 1
                    except:
                        idx = 0
                    lib_cbp_file = lib_cbp_files[idx]
                print("lib_cbp_file:", lib_cbp_file)
                lib_cbp_files_list.append(lib_cbp_file)
                lib_cbp_dir = os.path.dirname(lib_cbp_file)

                lib_files, lib_dirs = get_files_and_dirs(
                    project_root, lib_cbp_file, lib_cbp_dir
                )
                ff.write(
                    (
                        "add_library(%s STATIC\n"
                        % re.sub(
                            r"[^\w]+",
                            "_",
                            lib_cbp_dir.replace("\\", "/").replace(project_root, ""),
                        )
                    ).encode("utf-8")
                )
                for lib_file in lib_files:
                    lib_file = '       "${PROJECT_SOURCE_DIR}/%s"\n' % lib_file
                    ff.write(lib_file.encode("utf-8"))
                ff.write(b"       )\n")
                ff.write(
                    (
                        "target_include_directories(%s PUBLIC\n"
                        % re.sub(
                            r"[^\w]+",
                            "_",
                            lib_cbp_dir.replace("\\", "/").replace(project_root, ""),
                        )
                    ).encode("utf-8")
                )
                for lib_dir in lib_dirs:
                    lib_dir = (
                        lib_dir.replace("\\", "/")
                        .replace(project_root, "")
                        .strip("\\")
                        .strip("/")
                        .replace("\\", "/")
                    )
                    lib_dir = '              "${PROJECT_SOURCE_DIR}/%s"\n' % lib_dir
                    ff.write(lib_dir.encode("utf-8"))
                ff.write(b"              )\n")

            # libs
            libs = get_libs_a_dirs(project_root)
            if libs:
                ff.write(b"\nfile(GLOB libraries\n")
                for lib in libs:
                    lib = '  "${CMAKE_CURRENT_SOURCE_DIR}/%s/*.a"\n' % lib
                    ff.write(lib.encode("utf-8"))
                ff.write(b"  )\n")
                ff.write(b"target_link_libraries(${PROJECT_NAME} ${libraries})\n")

        # workspace
        cbps = [
            fname.replace("/", "\\")
            for fname in [
                cbp_file.replace(project_root + "/", "")
                for cbp_file in lib_cbp_files_list
            ]
            + [executable_cbp.replace(project_root + "/", "")]
        ]
        cbps = [f'  <Project filename="{fname}" />' for fname in cbps]
        workspace = executable_cbp.split("/")[-2]
        if "/" not in executable_cbp.replace(project_root + "/", ""):
            workspace = executable_cbp.split("/")[-1].split(".")[0]
        with open(
            rep(os.path.join(project_root, f"{workspace}.workspace")),
            "wb",
        ) as ff:
            ff.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
            ff.write(b"<CodeBlocks_workspace_file>\n")
            ff.write(b'  <Workspace title="Workspace">\n')
            ff.write(("\n".join(cbps).encode("utf-8")) + b"\n")
            ff.write(b"  </Workspace>\n")
            ff.write(b"</CodeBlocks_workspace_file>\n")

        # can not be in with block!
        os.system(
            "cd "
            + project_root
            # + r' && del /s /q .cache & rd /s /q .cache & del /s /q build & rd /s /q build & cmake -B build -G "MinGW Makefiles" -DCMAKE_EXPORT_COMPILE_COMMANDS=1 && cd build & copy compile_commands.json ..\ /y & cd ..'
            + r' && del /s /q build\\CMakeCache.txt & cmake -B build -G "MinGW Makefiles" -DCMAKE_EXPORT_COMPILE_COMMANDS=1 && cd build & copy compile_commands.json ..\ /y & timeout /t 3'
        )
