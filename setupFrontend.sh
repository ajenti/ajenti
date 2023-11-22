#!/bin/bash
#The script simplifies work with the Frontend of Ajenti Plugings
#Enables users to build and start one or multiple plugins

# List of available plugins - customize this array as needed.
PLUGINS=( "traffic" "dashboard" "shell" "fstab" "basicTemplate")

contains() {
    [[ $1 =~ (^|[[:space:]])$2($|[[:space:]]) ]]
    return $?
}

for plugin in "${PLUGINS[@]}"; do
    if ! contains "${PLUGINS[*]}" "shell"; then
      echo "Shell plugin isnt available exiting..."
       exit 1
    fi

done


if ! [ -x "$(command -v uname)" ]; then
  echo "Error: This script is intended for Unix-like environments." >&2
  exit 1
fi



OS="$(uname -s)"


find_yarn() {
  local yarn_path=$(command -v yarn || echo "")
  if [ -z "$yarn_path" ]; then
    echo "Yarn not found. Please provide the path to Yarn."
    read -r yarn_path
  fi
  echo "$yarn_path"
}

YARN_PATH=$(find_yarn)


if [ -z "$YARN_PATH" ]; then
  echo "Yarn path not set. Exiting."
  exit 1
fi

print_available_plugins() {
    echo "Available plugins:"
    for plugin in "${PLUGINS[@]}"; do
        echo "- $plugin"
    done
}

usage() {
    echo
    echo "Setup Frontend Tool"
    echo
    echo "Usage:"
    echo
    echo "link  : build the ngx-ajenti and create yarn link in each plugin"
    echo "start : starts yarn in all new ajenti plugins."
    echo "restart : restarts yarn in all new ajenti plugins."
    echo "kill : kill all ng serve."
    echo "build : builds ngx-ajenti library and restarts all yarn instances"
    echo
}

# Check if current directory is plugins-new
if [ "$(basename "$PWD")" != "plugins-new" ]; then
  echo "Not in plugins-new directory. Attempting to change directory..."
  if [ -d "plugins-new" ]; then
    cd "plugins-new" || {
      echo "Found plugins-new directory, but cannot change to it. Please check your permissions."
      exit 1
    }
  else
    echo "plugins-new directory not found. Please change to the plugins-new directory and run this script again."
    exit 1
  fi
fi


select_plugins() {
    echo "Available plugins:"
    for i in "${!PLUGINS[@]}"; do
        echo "[$i] ${PLUGINS[$i]}"
    done

    echo "Enter the numbers of the plugins you want to run, separated by spaces (e.g., 1 3):"
    read -ra user_input

    SELECTIONS=()
    for input in "${user_input[@]}"; do
        if [[ "$input" =~ ^[0-9]+$ ]] && (( input >= 0 && input < ${#PLUGINS[@]} )); then
            SELECTIONS+=("$input")
        else
            echo "Invalid selection: $input. Ignoring."
        fi
    done
}

run_selected() {
    select_plugins
    for index in "${SELECTIONS[@]}" ; do
        local plugin="${PLUGINS[$index]}"
        echo "Running selected plugin: $plugin"
        (cd "$plugin/frontend" && "$YARN_PATH" start) &
    done
    wait
}



start_yarn() {
    for p in "${PLUGINS[@]}" ; do
        echo $p
        cd "$p/frontend" || exit
        "$YARN_PATH" start &
        cd ../..
    done
}

kill_yarn() {
    if [ "$OS" = "Darwin" ] || [ "$OS" = "Linux" ]; then
        pkill -f "yarn start"
    else
        echo "Unsupported OS for killing Yarn processes. Please kill them manually."
        exit 1
    fi
}

build_and_link() {
    cd ngx-ajenti || exit
    ng build
    cd dist/ngx-ajenti || exit
    "$YARN_PATH" link
    cd ../../..
    for p in "${PLUGINS[@]}" ; do
        cd "$p/frontend" || exit
        rm -rf node_modules/@ngx-ajenti
        "$YARN_PATH" link @ngx-ajenti/core
        cd ../..
    done
}
build_ngx() {
    cd ngx-ajenti || exit
    ng build
    cd .. || exit
    rm -rf */frontend/.angular/cache
}
print_available_plugins
case $1 in
    start)
        start_yarn
        ;;
    link)
        build_and_link
        ;;
    build)
        kill_yarn
        build_ngx
        start_yarn
        ;;
    restart)
        kill_yarn
        start_yarn
        ;;
    kill)
        kill_yarn
        ;;
    help)
        usage
        ;;
    selected)
        run_selected
        ;;
    *)
        usage
        echo "$1 : option unknown...quitting"
        exit 1
        ;;
esac