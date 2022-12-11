#!/usr/bin/env python3
import json
import os
import shutil
import types

import jinja2
import yaml


data = {}


# python


def run(path):
    with open(path) as f:
        module = types.ModuleType('module')

        cwd = os.getcwd()
        os.chdir(os.path.dirname(path))
        exec(f.read(), module.__dict__)
        os.chdir(cwd)

        data = {}
        for k, v in module.__dict__.items():
            if k[:2] != "__" and k.isupper():
                data[k.lower()] = v

        return data


# shell


def cp(source, target):
    shutil.copytree(source, target) 


def mkdir(path):
    os.makedirs(path)


def rm(path):
    shutil.rmtree(path, ignore_errors=True)


# template


def render(path, template, template_data={}):
    env = jinja2.Environment(loader=jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(searchpath="."),
        jinja2.FileSystemLoader(searchpath=".")
    ]))

    _template = env.get_template(template)

    output = _template.render(**template_data).strip()
    with open(path, 'w+') as f:
        f.write(output)


# data


def load(path):
    basename = os.path.basename(path)

    if os.path.isdir(path):
        for filename in os.listdir(path):
            _data = _load_path(os.path.join(path, filename))
    
            if basename not in data:
                data[basename] = {}

            name = filename.split(".")
            data[basename][name[0]] = _data
    else:
        # TODO
        pass

def _load_path(path):
    if path.endswith(".json"):
        return _load_json(path)

    if path.endswith(".yaml"):
        return _load_yaml(path)


def _load_json(path):
    with open(path) as f:
        return json.loads(f.read())


def _load_yaml(path):
    with open(path) as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)
