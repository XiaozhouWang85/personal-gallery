import os

import yaml

YAML_FILE = 'app.yaml'

def replace_env_variables_in_app_yaml_file():

    with open(YAML_FILE, "r") as stream:
        yaml_data = yaml.safe_load(stream)

    if "env_variables" not in yaml_data:
        raise Exception("cannot find the \"env_variables\" section in yaml-file")

    for key in yaml_data["env_variables"]:
        env_var = yaml_data["env_variables"][key]
        if type(env_var) is str and env_var.startswith("$"):
            repl_env_var = os.environ.get(env_var[1:])
            if repl_env_var is not None:
                yaml_data["env_variables"][key] = repl_env_var
            else:
                raise Exception(f"cannot find the env-variable {env_var[1:]} in \"env\" section in github workflow")

    with open(YAML_FILE, "w") as stream:
        yaml.dump(yaml_data, stream)


if __name__ == "__main__":
    replace_env_variables_in_app_yaml_file()