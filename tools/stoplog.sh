#!/system/bin/sh
# stoplog.sh: stop running perflog.sh instances. Usage: su -c sh /data/local/tmp/stoplog.sh [duration]
# Matches on the duration argument if given (e.g. "1200"), otherwise stops all.
ps -A -o PID,ARGS | while read -r pid cmd; do
    case "$cmd" in
        "sh /data/local/tmp/perflog.sh ${1}"*) kill "$pid" && echo "stopped $pid: $cmd" ;;
    esac
done
