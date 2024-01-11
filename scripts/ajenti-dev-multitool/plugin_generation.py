import argparse
import asyncio
import concurrent.futures
from enum import Enum
import json
import os
import re
import shutil
import sys
from typing import List, Optional, Tuple


class TemplateFolder(Enum):
    MINIMAL = 'minimalTemplate'
    BASIC = 'basicTemplate'
    WIDGET = 'widgetTemplate'


func = lambda s: s[:1].upper() + s[1:] if s else ''


def __modify_port_in_angular_json(directory: str, project_name: str, new_port: int) -> None:
    angular_json_path = os.path.join(directory, 'angular.json')
    try:
        with open(angular_json_path, 'r') as file:
            config = json.load(file)

        project_config = config['projects'].get(project_name)
        if project_config:
            project_config['architect']['serve']['options']['port'] = new_port

            with open(angular_json_path, 'w') as file:
                json.dump(config, file, indent=2)
        else:
            print(f"Project {project_name} not found in angular.json")
    except FileNotFoundError:
        print(f"angular.json not found in {directory}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in {angular_json_path}")


def __replace_port_pattern( file_path, new_port, pattern=r'http://localhost:420\d+/'):
    # Read in the file
    with open(file_path, 'r') as file:
        file_data = file.read()

    # Replace the target pattern with the new port
    new_url = f"http://localhost:{new_port}/"
    file_data = re.sub(pattern, new_url, file_data)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(file_data)


def __rename_directory( directory: str, template_name: str, new_name: str) -> None:
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if template_name in file:
                new_file_path = os.path.join(root, file.replace(template_name, new_name))
                os.rename(os.path.join(root, file), new_file_path)
                print(f"Renamed file to {new_file_path}")


def __get_subdirectories( path: str) -> List[str]:
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]


def __get_port_number( directory: str) -> Optional[int]:
    angular_json_path = os.path.join(directory, 'angular.json')
    if os.path.exists(angular_json_path):
        with open(angular_json_path, 'r') as file:
            config = json.load(file)
        first_project = next(iter(config['projects']))
        return config['projects'][first_project]['architect']['serve']['options']['port']
    return None


def __find_greatest_port( directory):
    list_of_plugins = __get_subdirectories(directory)
    ports = {}
    for dir in list_of_plugins:
        port = __get_port_number(os.path.join(directory, os.path.join(dir, 'frontend')))
        if port is not None:
            ports[dir] = port
    return max(ports.values())


def __replace_in_files( replacements: List[Tuple[str, str, str]]) -> None:
    for file_path, old_string, new_string in replacements:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                contents = file.read()
                contents = contents.replace(old_string, new_string)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(contents)

            print(f"Replaced '{old_string}' with '{new_string}' in {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


def __rename_files( path: str, old_name: str, new_name: str) -> None:
    """
    Rename files in the directory tree starting at root_path
    by replacing old_name with new_name in the file names.
    """
    # Walk through the directory
    for path, dirs, files in os.walk(path, topdown=False):
        # Rename files
        for name in files:
            if old_name in name:
                new_file_name = name.replace(old_name, new_name)
                old_file_path = os.path.join(path, name)
                new_file_path = os.path.join(path, new_file_name)
                try:
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed {old_file_path} to {new_file_path}")
                except OSError as e:
                    print(f"Error renaming {old_file_path} to {new_file_path}: {e}")


def __rename_folders( root_path: str, new_name: str, template_name: str) -> None:
    """
    Rename specific folders within a project structure according to a new name.
    """
    base_path = os.path.abspath(root_path)
    paths = [
        (
            os.path.join(base_path, 'frontend', 'src', 'app', template_name, 'view', template_name),
            os.path.join(base_path, 'frontend', 'src', 'app', 'basicTemplate', 'view', new_name)
        ),
        (
            os.path.join(base_path, 'frontend', 'src', 'app', template_name),
            os.path.join(base_path, 'frontend', 'src', 'app', new_name)
        ),
    ]

    for path, new_path in paths:
        if os.path.exists(path):
            try:
                os.rename(path, new_path)
                print(f"Renamed {path} to {new_path}")
            except OSError as e:
                print(f"Error renaming {path} to {new_path}: {e}")
        else:
            print(f"The path {path} does not exist.")


async def __copy_directory(src: str, dst: str) -> None:
    """
    Asynchronously copies a directory from src to dst.
    """
    await asyncio.run(shutil.copytree(src, dst))


def __copy_plugin(new_plugin: str, template_folder: str, path_to_plugins_new: str) -> None:
    """
    Creates a new plugin by copying an existing template. The port and other configurations
    should be set externally if required.
    """
    new_folder_path = os.path.join(path_to_plugins_new, new_plugin)
    if os.path.exists(new_folder_path):
        print(f"Folder already exists: {new_folder_path}")
        exit(1)

    existing_folder_path = os.path.join(path_to_plugins_new, template_folder)
    try:
        # Use ThreadPoolExecutor to copy the directory
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the copy task
            future = executor.submit(shutil.copytree, existing_folder_path, new_folder_path)
            # Wait for the copy task to complete
            future.result()
    except Exception as e:
        print(f"An error occurred during copying: {e}")


def __construct_plugin_naming_convention( old_name: str = None, new_name: str = None):
    base_name = "ajenti-"
    plugin_suffix = "-plugin"
    template_base = old_name
    components = ["Component", "Service", "Module", "SideItemProvider"]

    # Basic naming convention without 'basic'
    naming_convention = {
        "template": f"{base_name}basicTemplate{plugin_suffix}",
        "component": "Component",
        "service": "Service",
        "module": "Module",
        "side_item_provider": "SideItemProvider"
    }

    # If old_name and new_name are provided, create specific conventions
    if old_name and new_name:
        old_names = {
            key: f"{base_name}{old_name}{plugin_suffix}" if key == "template"
            else old_name + naming_convention[key]
            for key in naming_convention
        }
        new_names = {
            key: f"{base_name}{new_name}{plugin_suffix}" if key == "template"
            else new_name + naming_convention[key]
            for key in naming_convention
        }
        return old_names, new_names, template_base


def __handel_backend_modifications( new_folder_path: str, old_name: str, new_name: str):
    if not new_folder_path.endswith(f"/{new_name}"):
        new_folder_path = os.path.join(new_folder_path, new_name)
    __rename_files(path=f"{new_folder_path}/backend", old_name=old_name, new_name=new_name)
    replacements = [
        (os.path.join(new_folder_path, f'backend/controllers/{new_name}.py'),
         old_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'backend/__init__.py'),
         old_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'plugin.yml'),
         old_name,
         new_name
         ),
    ]
    __replace_in_files(replacements)



def __handel_frontend_modifications( new_folder_path: str, old_name: str, new_name: str, port: int):
    template_naming, new_plugin_naming, basic_template_name = __construct_plugin_naming_convention(old_name,new_name)
    new_parent_folder_path = new_folder_path
    new_folder_path = os.path.join(new_folder_path, new_name)

    replacements = [
        (os.path.join(new_folder_path, 'plugin.yml'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'plugin.yml'),
         func(template_naming["module"]),
         new_plugin_naming["module"]
         ),
        (os.path.join(new_folder_path, 'frontend/package.json'),
         template_naming["template"].lower(),
         new_plugin_naming["template"]
         ),
        (os.path.join(new_folder_path, 'frontend/angular.json'),
         template_naming["template"],
         new_plugin_naming["template"]
         ),
        (os.path.join(new_folder_path, 'frontend/webpack.config.js'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/app.component.ts'),
         func(template_naming["template"]),
         new_plugin_naming["template"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/app.module.ts'),
         func(template_naming["module"]),
         new_plugin_naming["module"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/app.module.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/app-routing.module.ts'),
         func(template_naming["module"]),
         new_plugin_naming["module"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/app-routing.module.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/basicTemplate.module.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/basicTemplate.module.ts'),
         func(template_naming["module"]),
         new_plugin_naming["module"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/basicTemplate.module.ts'),
         func(template_naming["component"]),
         new_plugin_naming["component"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/basicTemplate.routes.ts'),
         func(template_naming["component"]),
         new_plugin_naming["component"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/basicTemplate.routes.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/services/basicTemplate.service.ts'),
         func(template_naming["service"]),
         new_plugin_naming["service"]
         ),
        (os.path.join(new_folder_path, 'frontend/src/app/basicTemplate/services/basicTemplate.service.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path,
                      'frontend/src/app/basicTemplate/view/basicTemplate/basicTemplate.component.ts'),
         basic_template_name,
         new_name
         ),
        (os.path.join(new_folder_path,
                      'frontend/src/app/basicTemplate/view/basicTemplate/basicTemplate.component.ts'),
         func(template_naming["component"]),
         new_plugin_naming["component"]
         ),
        (os.path.join(new_folder_path,
                      'frontend/src/app/basicTemplate/view/basicTemplate/basicTemplate.component.ts'),
         func(template_naming["service"]),
         new_plugin_naming["service"]
         ),
        (os.path.join(new_folder_path,
                      'frontend/src/app/basicTemplate/basicTemplate.routes.ts'),
         f"{old_name.upper()}_ROUTES",
         f"{new_name.upper()}_ROUTES"
         ),
        (os.path.join(new_folder_path,
                      'frontend/src/app/basicTemplate/basicTemplate.module.ts'),
         f"{old_name.upper()}_ROUTES",
         f"{new_name.upper()}_ROUTES"
         ),
        (os.path.join(new_folder_path, f'backend/{new_name}_sidebar_item_provider.py'),
         func(template_naming["side_item_provider"]),
         new_plugin_naming["side_item_provider"]
        ),
        (os.path.join(new_folder_path, f'backend/{new_name}_sidebar_item_provider.py'),
         basic_template_name,
         new_name
        ),
    ]
    __replace_in_files(replacements)
    __rename_files(new_folder_path, basic_template_name, new_name)
    __rename_folders(new_folder_path, new_name, basic_template_name)
    if port is None:
        port = __find_greatest_port(new_parent_folder_path) + 1
    print("Used Port Number", port)
    __modify_port_in_angular_json(os.path.join(new_folder_path, 'frontend/'), new_plugin_naming["template"], port)

    file_path = os.path.join(new_folder_path, 'plugin.yml')  # The file where the port number is to be replaced
    __replace_port_pattern(file_path, port)


def clone_plugin(new_folder_path: str, new_name: str, old_name: str, template_folder: str,
                 path_to_plugins_new: str, port: Optional[int] = None) -> None:
    __copy_plugin(new_plugin=new_name,
                       template_folder=template_folder,
                       path_to_plugins_new=path_to_plugins_new)

    if old_name == "minimalTemplate":
        __handel_backend_modifications(new_folder_path=new_folder_path,
                                            old_name=old_name,
                                            new_name=new_name)
    if old_name == "basicTemplate":
        __handel_backend_modifications(new_folder_path=new_folder_path,
                                            old_name=old_name,
                                            new_name=new_name)
        __handel_frontend_modifications(new_folder_path=new_folder_path,
                                             old_name=old_name,
                                             new_name=new_name,
                                             port=port)
    if old_name == "widgetTemplate":
        print("create a new widget template")


def create_new_plugin_minimal(name, port):
    path_to_template = os.path.join(os.path.dirname(os.getcwd()), 'plugin-templates', TemplateFolder.MINIMAL.value)
    path_to_generate = os.path.join(os.path.dirname(os.getcwd()), 'plugins-new')
    path_to_new_plugin = os.path.join(os.path.dirname(os.getcwd()), f'plugins-new/{name}')
    clone_plugin(new_folder_path=path_to_new_plugin,
                 new_name=name,
                 old_name=TemplateFolder.MINIMAL.value,
                 template_folder=path_to_template,
                 path_to_plugins_new=path_to_generate,
                 port=port)


def create_new_plugin_default(name, port):
    path_to_template = os.path.join(os.path.dirname(os.getcwd()), 'plugin-templates', TemplateFolder.BASIC.value)
    path_to_generate = os.path.join(os.path.dirname(os.getcwd()), 'plugins-new')
    clone_plugin(new_folder_path=path_to_generate,
                 new_name=name,
                 old_name=TemplateFolder.BASIC.value,
                 template_folder=path_to_template,
                 path_to_plugins_new=path_to_generate,
                 port=port
                 )


def create_new_plugin_by_cli_arguments():
    parser = argparse.ArgumentParser(description='Ajenti Dev Multitool')

    command_pattern = re.compile(r'--new-plugin-?(\w*)')

    args = sys.argv[1:]
    match = None

    for arg in args:
        match = command_pattern.match(arg)
        if match:
            break

    if match:
        print(os.getcwd())
        command_name = match.group(1)
        remaining_args = args[args.index(arg) + 1:]

        if command_name == 'minimal':
            parser.add_argument('name', help='Name of the plugin')
            parser.add_argument('-p', '--port', type=int, help='Port number')
        elif command_name == '':
            command_name = ''
            parser.add_argument('name', help='Name of the plugin')
            parser.add_argument('-p', '--port', type=int, help='Port number')

        args = parser.parse_args(remaining_args)
        args.command = f'new-plugin-{command_name}'
        if args.command == 'new-plugin-minimal':
            create_new_plugin_minimal(args.name, args.port)
        elif args.command == 'new-plugin-':
            create_new_plugin_default(args.name, args.port)
        else:
            print('Invalid command')
