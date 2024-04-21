import importlib.util
import sys
import string
import secrets
import json
from inspect import getmembers, isfunction

def gensym(length=32, prefix="gensym_"):
    """
    generates a fairly unique symbol, used to make a module name,
    used as a helper function for load_module

    :return: generated symbol
    """
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    symbol = "".join([secrets.choice(alphabet) for i in range(length)])

    return prefix + symbol

def load_module(source, module_name=None):
    """
    reads file source and loads it as a module

    :param source: file to load
    :param module_name: name of module to register in sys.modules
    :return: loaded module
    """

    if module_name is None:
        module_name = gensym()

    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    manifest = json.loads(module.get_manifest())

    func = dict(getmembers(module, isfunction))[manifest["name"]]
    
    return func, module.get_manifest()

# python to read a file from a directory
def read_files_from_directory(directory):
    import os
    # filter only .py files
    files = [f"{directory}/{f}" for f in os.listdir(directory) if f.endswith('.py')]

    return files

if __name__ == "__main__":
    print("utils module")