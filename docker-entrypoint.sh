#!/bin/sh
case ${1} in
    sub)
    echo "Starting sub"
    exec python mqtt_sub.py
    ;;
    pub)
    echo "Starting pub"
    exec python sacn_mqtt.py
    ;;
    *)
    exec "$@"
    ;;
esac
