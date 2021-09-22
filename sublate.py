#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import shutil
import types

import jinja2
import yaml


def main():
    parser = argparse.ArgumentParser(prog='sublate')
    parser.add_argument('path', metavar='path', type=str, nargs='?', default='.', help='path to project')
    parser.add_argument('--data', metavar='data', type=str, nargs='*', help='path to data')
    parser.add_argument('--output', metavar='output', type=str, nargs='?', default='output', help='path to output')
    parser.add_argument('--render', metavar='render', type=str, nargs='*', help='files to render')
    parser.add_argument('--remove', metavar='remove', type=str, nargs='*', help='files to remove')

    args = parser.parse_args()

    data = {}
    if args.data:
        for data in args.data:
            data.update(get_project_data(args.data))

    build(args.path, args.output, args.render, args.remove, data)


# TODO: args.output should overwrite root sublate.yaml
def build(path, output_path, data=None, render=None, remove=None):
    if data is None:
        data = {}

    if render is None:
        render = []

    if remove is None:
        remove = []

    _build(path, output_path, data, render, remove, path)


def _build(path, output_path, data, render, remove, root_path):
    local_data = get_sublate_data(path)

    if "path" in local_data:
        path = os.path.join(path, local_data["path"])

    if "output" in local_data:
        if local_data["output"][0] == "/":
            output_path = local_data["output"]
        else:
            output_path = os.path.join(path, local_data["output"])

    if "data" in local_data:
        if type(local_data["data"]) is list:
            for d in local_data["data"]:
                if d[0] == "/":
                    data_path = d[0]
                else:
                    data_path = os.path.join(root_path, d["data"])

                data.update(get_project_data(data_path))
        else:
            if local_data["data"][0] == "/":
                data_path = local_data["data"][0]
            else:
                data_path = os.path.join(root_path, local_data["data"])

            data.update(get_project_data(data_path))

    if "remove" in local_data:
        if type(local_data["remove"]) is list:
            remove = local_data["remove"]
        else:
            remove = [local_data["remove"]]

    if "render" in local_data:
        if type(local_data["render"]) is list:
            render = local_data["render"]
        else:
            render = [local_data["render"]]

        root_path = path

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    print(f"Building: {path}")
    os.mkdir(output_path)

    if "path" in local_data and local_data["path"] not in [".", "./"]:
        _build(path, output_path, data, render, remove, root_path)
        return

    # TODO: skip over data and output paths
    for filename in os.listdir(path):
        if filename.startswith("sublate."):
            continue

        if filename in remove:
            continue

        full_path = os.path.join(path, filename)
        full_output_path = os.path.join(output_path, filename)

        if os.path.isdir(full_path):
            local_render = []
            for r in render:
                parts = r.split(os.sep)
                if filename == parts[0]:
                    local_render.append(os.path.join(*parts[1:]))

            _build(full_path, full_output_path, data, local_render, remove, root_path)
        else:
            for r in render:
                if fnmatch.fnmatch(filename, r):
                    env = jinja2.Environment(loader=jinja2.ChoiceLoader([
                        jinja2.FileSystemLoader(searchpath=path),
                        jinja2.FileSystemLoader(searchpath=root_path)
                    ]))

                    try:
                        template = env.get_template(filename)
                    except UnicodeDecodeError:
                        print(f"Cannot render binary file: {full_path}")
                        continue

                    output = template.render(**data).strip()
                    with open(full_output_path, 'w+') as f:
                        f.write(output)

                    break
            else:
                shutil.copy(full_path, full_output_path)


def get_project_data(path):
    data = {}

    if os.path.isdir(path):
        for filename in os.listdir(path):
            data.update(load_path(os.path.join(path, filename)))
    else:
        data.update(load_path(path))

    return data


def get_sublate_data(path):
    data = { }

    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.startswith("sublate."):
                data.update(load_path(os.path.join(path, filename)))
    else:
        data.update(load_path(path))

    return data


def load_path(path):
    if path.endswith(".json"):
        return load_json(path)

    if path.endswith(".yaml"):
        return load_yaml(path)

    if path.endswith(".py"):
        return load_py(path)


def load_json(path):
    with open(path) as f:
        return json.loads(f.read())


def load_yaml(path):
    with open(path) as f:
        return yaml.load(f.read(), Loader=yaml.FullLoader)


def load_py(path):
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


if __name__ == "__main__":
    main()
