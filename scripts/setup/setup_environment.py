#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import platform
import sys
import logging
import time
import venv

included_dirs = {'plugins', 'plugin-templates', 'plugins-new'}


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Setup Environment Tool')
    parser.add_argument('--setup', action='store_true', help='Perform setup operations.')
    return parser.parse_args()


def is_installed(command):
    return shutil.which(command) is not None


import subprocess
import platform
import sys


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check if command execution was successful
    if process.returncode != 0:
        print(f'Error executing command: {" ".join(command)}\n{stderr.decode()}')
        return stderr
    else:
        print(stdout.decode())
        return stdout


def install_node_yarn_angular_cli():
    import subprocess
    import os
    import platform

    os_name = platform.system()
    node_version = "16"
    angular_cli_version = "16.2.6"

    def is_installed(item):
        """
        Checks if item is installed.
        """
        try:
            subprocess.check_output(["which", item])
            return True
        except subprocess.CalledProcessError:
            return False

    if is_installed("node") and is_installed("yarn") and is_installed("ng"):
        print("Node.js, Yarn, and Angular CLI are already installed.")
        return

    try:
        if os_name == "Linux":
            print("Downloading nvm...")
            process = subprocess.Popen(
                'wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash', shell=True)
            process.wait()

            print("Generating install script...")
            with open('install.sh', 'w') as f:
                f.write("""
        source ~/.nvm/nvm.sh
        nvm install {node_version}
        nvm use {node_version}
        npm install --global yarn
        npm install --global @angular/cli@{angular_cli_version}
                        """.format(node_version=node_version, angular_cli_version=angular_cli_version))

            print("Running install script...")
            process = subprocess.Popen('bash install.sh', shell=True)
            process.wait()

            # Clean up the temporary install script
            print("Cleaning up...")
            subprocess.Popen('rm install.sh', shell=True)
            print("Node.js, Yarn, and Angular CLI installed successfully.")


        elif os_name == "Darwin":
            # Install Node.js and Yarn for macOS
            subprocess.run(["brew", "install", f"node@{node_version.split('.')[0]}"], check=True)
            subprocess.run(["brew", "link", "--overwrite", f"node@{node_version.split('.')[0]}", "--force"], check=True)
            subprocess.run(["brew", "install", "yarn"], check=True)
            subprocess.run(["npm", "install", "--global", f"@angular/cli@{angular_cli_version}"], check=True)

        else:
            print(
                f"Operating system '{os_name}' not supported for specific Node.js, Yarn, and Angular CLI installation.")
            sys.exit(1)

        # Install Angular CLI

        print("Node.js, Yarn, and Angular CLI installed successfully.")

    except subprocess.CalledProcessError:
        print("Failed to install Node.js, Yarn, and/or Angular CLI.")
        sys.exit(1)


def is_docker_running():
    try:
        subprocess.run(["docker", "info"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def install_requirements(requirements_path):
    """
    Install requirements from the given path.
    """
    print("Requirements from path")
    print(requirements_path)

    try:
        subprocess.run(['pip3', 'install', '-r', requirements_path], check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


def install_frontend_requirements(start_path):
    print("Installing Frontend requirements:")
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Exclude 'node_modules' and directories listed in included_dirs
        dirs[:] = [d for d in dirs if d != 'node_modules' and d not in included_dirs]

        # Check and install requirements in the remaining directories
        for file in files:
            if file in ['requirements.txt', 'requirements-rtd.txt']:
                requirements_path = os.path.join(root, file)
                install_requirements(requirements_path)


def start_docker():
    from python_on_whales import docker
    os_name = platform.system()
    try:
        if os_name == "Darwin" or os_name == "Linux":  # macOS
            try:

                docker.compose.build()
                docker.compose.up()
                print("Docker started successfully on Linux.")
            except ImportError:
                print("python-on-whales is not installed. Please install it first.")
                sys.exit(1)
        else:
            print("Operating system is not supported")
            exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Failed to start Docker: {e}")
        sys.exit(1)


def find_directory(start_path, target_directory_name):
    """
    Search for a directory with the specified name within the given path.

    :param start_path: The path to start searching from
    :param target_directory_name: The name of the directory to find
    :return: The path to the found directory or None if not found
    """
    for root, dirs, files in os.walk(start_path):
        if target_directory_name in dirs:
            return os.path.join(root, target_directory_name)
    return None


def start_backend(path):
    os_name = platform.system()
    try:
        start_docker()
        print("PATH", path)
        # Define the docker-compose command
        if os_name == "Linux":
            compose_command = ["docker", "compose", "up"]
        else:
            compose_command = ["docker-compose", "up", "-d"]  # Adjust the path as necessary
        subprocess.run(compose_command, check=True, cwd=path, shell=True)
        print("Backend started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start the backend: {e}")


if __name__ == "__main__":
    args = parse_arguments()


    if len(sys.argv) > 0:  # Check that at least one argument was given
        print(sys.argv[-1])
    else:
        print("No arguments were provided.")
        exit(1)

    path_to_plugins_new = find_directory(os.path.dirname(os.path.dirname(os.getcwd())), "plugins-new")
    start_directory = os.path.dirname(path_to_plugins_new)
    install_frontend_requirements(start_directory)
    install_node_yarn_angular_cli()

    start_backend(start_directory)
