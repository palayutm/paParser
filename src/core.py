import os
import time
import shutil
import subprocess
import requests
from subprocess import PIPE
from colorclass import Color
from pathlib import Path

import yaml
from .codeforces_parser import CodeforcesParser
from .pe_parser import PEParser
from .atcoder_parser import AtCoderParser

CXX_FLAGS = "-std=c++2a -O2 -DDEBUG -g -fsanitize=address -fno-omit-frame-pointer"


def write_problem(data):
    odir = data["file_name"]
    if os.path.exists(odir):
        return "%s exists, skip" % odir
    os.makedirs(odir)
    yaml_path = os.path.join(odir, "info.yml")
    code_path = os.path.join(data["file_name"] + ".cc")
    template_path = "../template/template.cc"
    if os.path.exists(template_path):
        shutil.copyfile(template_path, code_path)
    else:
        open(code_path, "a").close()
    with open(yaml_path, "w") as fp:
        yaml.dump(data, fp, default_flow_style=False, default_style="|")
    for k, v in data.items():
        if k.startswith("sample_in"):
            name = k[9:]
            in_txt, out_txt = v, data["sample_out" + name]
            open(os.path.join(odir, name + ".in"), "w").write(
                in_txt + "\n========\n" + out_txt
            )
    return data


def parse_problem(url, page=None):
    if page is None:
        page = requests.get(url).text
    parsers = [CodeforcesParser(), PEParser(), AtCoderParser()]
    for parser in parsers:
        if parser.match(url):
            content = parser.parse(url, page)
            content["date"] = time.strftime("%Y-%m-%d", time.localtime())
            return write_problem(content)

    return {"error": "No parser found to process this page."}


def test_problem(code_path, samples):
    run_dir = ".run_dir"
    os.makedirs(run_dir, exist_ok=True)
    exec_name = os.path.join(run_dir, "a.out")
    compile_cmd = ["g++", code_path, "-o", exec_name]
    compile_cmd.extend(CXX_FLAGS.split())
    if subprocess.Popen(compile_cmd).wait() != 0:
        return
    name, result = [], []

    sample_dir = Path(os.path.splitext(code_path)[0])

    for sample in sorted(sample_dir.glob("*.in")):
        name.append(sample)
        if len(samples) == 0 or os.path.splitext(sample.name)[0] in samples:
            sample_in, sample_out = [], []
            cur = sample_in
            for line in open(sample):
                line = line.strip()
                if line.startswith("========"):
                    cur = sample_out
                else:
                    cur.append(line)
            sample_in = "\n".join(sample_in)
            sample_out = "\n".join(sample_out)

            print('Test "%s:"' % sample)
            print("input:")
            print(sample_in)
            print("\nExpected output:")
            print(sample_out)
            print("\nExecution result:")
            t = subprocess.Popen(exec_name, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout_data, stderr_data = t.communicate(
                input=bytes(sample_in, encoding="utf-8")
            )
            stdout_data = str(stdout_data, encoding="utf-8").strip()
            stderr_data = str(stderr_data, encoding="utf-8").strip()
            stdout_data = "\n".join([_.strip() for _ in stdout_data.split("\n")])
            print(stdout_data)
            print("\nStderr output:")
            print(stderr_data)
            if len(sample_out) == 0:
                print("Verdict: UNKNOWN")
                result.append(Color("UNKNOWN"))
            elif stdout_data == sample_out:
                print("Verdict: PASSED")
                result.append(Color("{autogreen}PASSED{/autogreen}"))
            else:
                print("Verdict: FAILED")
                result.append(Color("{autored}FAILED{/autored}"))
            print("-" * 80)
        else:
            result.append("SKIP")
    print("=" * 80)
    for n, x in zip(name, result):
        print('Test "%s": %s' % (n, x))


def archive_problem(code_path):
    sample_dir = Path(os.path.splitext(code_path)[0])
    with open(sample_dir / "info.yml") as fp:
        meta = yaml.load(fp, Loader=yaml.FullLoader)

    archive_dir = Path("../archive")
    archive_dir /= "-".join(meta["date"].split("-")[:-1])
    archive_dir /= " - ".join([meta["date"], meta["contest_name"]])

    shutil.move(sample_dir, archive_dir / meta["file_name"])
    shutil.move(code_path, archive_dir / (meta["file_name"] + ".cc"))
    print("Archive to:", archive_dir.resolve())
