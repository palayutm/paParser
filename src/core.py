import os
import yaml
import time
import shutil
import subprocess
import requests
from subprocess import PIPE
from colorclass import Color
from .codeforces_parser import CodeforcesParser
from .pe_parser import PEParser
from .atcoder_parser import AtCoderParser

WORK_DIR = os.getcwd()
YAML_PATTERN = 'meta_info_%s.yaml'
CXX_FLAGS = '-O2 -std=c++17'


def write_problem(data):
    yaml_path = YAML_PATTERN % data['file_name']
    code_path = data['file_name'] + '.cc'
    template_path = os.path.join(WORK_DIR, '../template/template.cc')
    if os.path.exists(template_path):
        shutil.copyfile(template_path, code_path)
    else:
        open(os.path.join(WORK_DIR, code_path), 'a').close()
    with open(yaml_path, 'w') as fp:
        yaml.dump(data, fp, default_flow_style=False, default_style='|')


def load_problem(code_path):
    file_name = os.path.splitext(code_path)[0]
    with open(YAML_PATTERN % file_name) as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def parse_problem(url, page=None):
    if page is None:
        page = requests.get(url).text
    parsers = [CodeforcesParser(), PEParser(), AtCoderParser()]
    for parser in parsers:
        if parser.match(url):
            content = parser.parse(url, page)
            content['date'] = time.strftime("%Y-%m-%d", time.localtime())
            if os.path.exists(content['file_name'] + '.cc'):
                return {
                    'error': 'file %s exists, remove first.' % (os.path.join(WORK_DIR, content['file_name'] + '.cc'))
                }
            write_problem(content)
            return content

    return {'error': 'No parser found to process this page.'}


def test_problem(code_path, indexes):
    run_dir = os.path.join(WORK_DIR, '.run_dir')
    os.makedirs(run_dir, exist_ok=True)
    exec_name = os.path.join(run_dir, 'a.out')
    compile_cmd = ['g++', code_path, '-o', exec_name]
    compile_cmd.extend(CXX_FLAGS.split())
    if subprocess.Popen(compile_cmd).wait() != 0:
        return
    meta = load_problem(code_path)
    case_num = 0
    result = []
    while True:
        if 'sample_in%i' % case_num not in meta:
            break
        if len(indexes) == 0 or case_num in indexes:
            sample_in = meta['sample_in%i' % case_num]
            sample_out = meta.get('sample_out%i' % case_num, None)
            print('Test #%i:' % case_num)
            print('input:')
            print(sample_in)
            print('\nExpected output:')
            print(sample_out)
            print('\nExecution result:')
            t = subprocess.Popen(exec_name, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout_data, stderr_data = t.communicate(input=bytes(sample_in, encoding='utf-8'))
            stdout_data = str(stdout_data, encoding='utf-8').strip()
            stderr_data = str(stderr_data, encoding='utf-8').strip()
            stdout_data = '\n'.join([_.strip() for _ in stdout_data.split('\n')])
            print(stdout_data)
            print('\nStderr output:')
            print(stderr_data)
            if sample_out is None:
                print('Verdict: UNKNOWN')
                result.append(Color('UNKNOWN'))
            elif stdout_data == sample_out:
                print('Verdict: PASSED')
                result.append(Color('{autogreen}PASSED{/autogreen}'))
            else:
                print('Verdict: FAILED')
                result.append(Color('{autored}FAILED{/autored}'))
            print('-' * 80)
        else:
            result.append('SKIP')
        case_num += 1
    print('=' * 80)
    for i in range(len(result)):
        print('Test #%i: ' % i + result[i])


def archive_problem(code_path):
    meta = load_problem(code_path)
    archive_dir = os.path.join(WORK_DIR, '../archive', '-'.join(meta['date'].split('-')[:-1]),
                               ' - '.join([meta['date'], meta['contest_name']]))
    os.makedirs(archive_dir, exist_ok=True)
    yaml_path = YAML_PATTERN % os.path.splitext(code_path)[0]
    target_code_path = os.path.join(archive_dir, code_path)
    target_yaml_path = os.path.join(archive_dir, yaml_path)
    if os.path.exists(target_code_path):
        print('path %s exists, skip' % target_code_path)
    else:
        shutil.move(code_path, target_code_path)
        shutil.move(yaml_path, target_yaml_path)
        print('Archive to: ' + os.path.abspath(archive_dir))
