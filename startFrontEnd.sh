#! /bin/bash
# BAD HARDCODED THINGS
cd plugins-new
PLUGINS=( "traffic" "dashboard" "shell" "fstab" )
######################
usage () {
    echo 
    echo "Little yarn plugin manager"
    echo 
    echo "Usage:"
    echo
    echo "yarnmanager start : starts yarn in all new ajenti plugins."
    echo
    echo "yarnmanager restart : restarts yarn in all new ajenti plugins."
    echo
    echo "yarnmanager kill : kill all ng serve."
    echo
    echo "yarnmanager build : builds ngx-ajenti library and restarts all yarn instances"
    echo
}
start_yarn () {
    for p in "${PLUGINS[@]}" ; do
        cd $p/frontend
        /opt/homebrew/bin/yarn start &
        cd ../..
    done
}
kill_yarn () {
    /usr/bin/killall node
    for pid in $(pgrep -f "ng serve") ; do
        kill $pid
    done
}
build_ngx () {
    cd ngx-ajenti
    ng build
    cd ..
    rm -rf */frontend/.angular/cache
}
case $1 in
    start)
        start_yarn
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
    *)
        usage
        echo "$1 : option unknown...quitting"
        ;;
esac