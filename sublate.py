#!/usr/bin/env python3
import datetime
import glob
import json
import os
import shutil
import subprocess
import types

import jinja2
import yaml


data = {}
root = os.getcwd()


def run(pathname):
    for path in glob.glob(pathname):
        if path.endswith(".py"):
            with open(path) as f:
                module = types.ModuleType('module')

                cwd = os.getcwd()
                os.chdir(os.path.dirname(path))
                exec(f.read(), module.__dict__)
                os.chdir(cwd)
        else:
            subprocess.run([path])


def cp(source, target):
    if os.path.isdir(source):
        shutil.copytree(source, target) 
    else:
        shutil.copfile(source, target) 


def mkdir(path):
    os.makedirs(path)


def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        os.remove(path)


def render(path, template, template_data={}):
    env = jinja2.Environment(loader=jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(searchpath="."),
        jinja2.FileSystemLoader(searchpath=root)
    ]))

    _template = env.get_template(template)

    output = _template.render(**(data | template_data)).strip()
    with open(path, 'w+') as f:
        f.write(output)


def read(pathname):
    _data = {}
    for path in glob.glob(pathname):
        with open(path) as f:
            if path.endswith(".json"):
                _data[path] = json.loads(f.read())

            if path.endswith(".yaml"):
                _data[path] = yaml.load(f.read(), Loader=yaml.FullLoader)
    
    return _data


def date_iso():
    return datetime.datetime.now().isoformat()
