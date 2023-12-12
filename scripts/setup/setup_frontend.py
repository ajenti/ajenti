import os
import shutil
import argparse
import subprocess
import psutil
import signal
import sys

# List of available plugins - customize this array as needed.
PLUGINS = ["traffic", "dashboard", "shell"]
serve_process = []

def find_yarn():
    yarn_path = shutil.which("yarn")
    print("Yarn path: ", yarn_path)
    if yarn_path is None:
        print("Yarn not found. Please provide the path to Yarn.")
        yarn_path = input().strip()
    return yarn_path


def usage():
    print("\nSetup Frontend Tool\n")
    print("Usage:\n")
    print("start : starts yarn in all new ajenti plugins.")
    print("build : builds ngx-ajenti library and restarts all yarn instances")
    print()


def kill_yarn(os_name):
    pattern = 'ng serve'
    if os_name in ["Darwin", "Linux"]:
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            # Ensure cmdline is a list or iterable
            if process.info['cmdline'] and isinstance(process.info['cmdline'], (list, tuple)):
                cmdline = ' '.join(process.info['cmdline'])
                if pattern in cmdline:
                    print(f"Killing process: {process.info['pid']} - {cmdline}")
                    try:
                        process.terminate()
                        process.wait(timeout=5)  # Wait for graceful termination
                        if process.is_running():
                            print(f"Forcefully killing process: {process.info['pid']}")
                            process.kill()
                    except Exception as e:
                        print(f"Error terminating process {process.info['pid']}: {e}")
    else:
        print("Unsupported OS for killing Yarn processes. Please kill them manually.")


def build(yarn_path):
    print(os.getcwd())
    os.chdir("ngx-ajenti")
    subprocess.run([yarn_path, "install"])
    subprocess.run([yarn_path, "run", "build"])
    os.chdir("..")
    for plugin in PLUGINS:
        os.chdir(f"{plugin}/frontend")
        subprocess.run([yarn_path, "run", "build"])
        os.chdir("../..")


def prepare_requirements_and_start_all_plugins(yarn_path):
    os.chdir("ngx-ajenti")
    # Set yarn as the default package manager
    subprocess.run(['ng', 'config', '-g', 'cli.packageManager', 'yarn'])
    subprocess.run([yarn_path, "install"])
    subprocess.run([yarn_path, "run", "build"])
    os.chdir("dist/ngx-ajenti")
    subprocess.run([yarn_path, "link"])
    os.chdir("../../..")
    for plugin in PLUGINS:
        os.chdir(f"{plugin}/frontend")
        cache_path = os.path.join(".angular", "cache")
        if os.path.exists(cache_path):
            subprocess.run(["rm", "-rf", cache_path])
        subprocess.run([yarn_path, "install"])
        # Create a symbolic link to the ngx-ajenti library
        print("LINKING", plugin)
        node_modules_path = os.path.join(plugin, "frontend", "node_modules", "@ngx-ajenti")
        if os.path.exists(node_modules_path):
            subprocess.run(["rm", "-rf", node_modules_path])
        subprocess.run([yarn_path, "link", "@ngx-ajenti/core"])
        # Copy the proxy.conf.template.json file to proxy.conf.json
        print("COPY PROXY", plugin)
        if not os.path.isfile('proxy.conf.json'):
            print("COPY PROXY_TEMPLATE", plugin)
            shutil.copyfile('proxy.conf.template.json', 'proxy.conf.json')
        # Run the plugin
        print("YARN START", plugin)
        proc = subprocess.Popen([yarn_path, "start"])
        serve_process.append(proc)
        os.chdir("../..")


def ensure_correct_directory(expected_directory):
    current_directory = os.path.basename(os.getcwd())
    if current_directory != expected_directory:
        try:
            parent_directory = os.path.dirname(os.path.dirname(os.getcwd()))
            expected_path = os.path.join(parent_directory, expected_directory)
            if os.path.isdir(expected_path):
                os.chdir(expected_path)
            else:
                print(
                    f"{expected_directory} directory not found in {parent_directory}. Please navigate to the correct directory and run this script again.")
                sys.exit(1)
        except Exception as e:
            print(f"Error changing directory: {e}")
            sys.exit(1)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Cleaning up before exit...')

    for proc in serve_process:
        try:
            proc.terminate()
        except Exception as e:
            print(f"Error terminating plugin process {proc.pid}: {e}")
    sys.exit(0)

def main():
    ensure_correct_directory("plugins-new")

    # Finds the yarn path
    yarn_path = find_yarn()
    # Checks if shell plugin is available
    if "shell" not in PLUGINS:
        print("Shell plugin isn't available, exiting...")
        sys.exit(1)

    if not yarn_path:
        print("Yarn path not set. Exiting.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Setup Frontend Tool')
    parser.add_argument('--start', action='store_true')
    parser.add_argument('--build', action='store_true')

    args = parser.parse_args()

    if args.start:
        prepare_requirements_and_start_all_plugins(yarn_path)
        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
    elif args.build:
        build(yarn_path)
    else:
        usage()
        print("Option unknown...quitting script")
        sys.exit(1)


if __name__ == "__main__":
    main()
