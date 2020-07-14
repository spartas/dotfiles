#!/usr/bin/env bash

DEBUG=0
DRIVER_VERSION="450.57"

INSTALLED_VERSION=$(modinfo -F version nvidia)

OPTS="--no-cc-version-check --silent --dkms"
echo "$OPTS"

systemctl list-units --type target | grep -q "^graphical"  
if [ $? -eq 1 ]
then
  DEBUG=0
else
  DEBUG=1
fi

echo ${DEBUG}

CMD_ACTION=""
while getopts "k:pr" OPTION; do
  case "${OPTION}" in
    k)
      # Can only be used with an existing driver matching the same version
      OPTS="${OPTS} --kernel-module-only --kernel-name=${OPTARG} --no-x-check --dkms"
      ;;
    p)
      if [ -n "${CMD_ACTION}" ]
      then
        echo "Only one of -p (poweroff) or -r (reboot) should be specified."
	exit 1
      fi

      CMD_ACTION="systemctl poweroff"
      ;;
    r)
      if [ -n "${CMD_ACTION}" ]
      then
        echo "Only one of -p (poweroff) or -r (reboot) should be specified."
	exit 1
      fi
      CMD_ACTION="systemctl reboot"
      ;;
  esac
done

BIN=/path/to/nvidia/installer/NVIDIA-Linux-x86_64-${DRIVER_VERSION}.run
STATUS_INSTALL=-1

date
echo ${BIN} ${OPTS}
if [ $DEBUG -eq 0 ]
then
  ${BIN} ${OPTS}
  STATUS_INSTALL=$?
fi
date

if [ $STATUS_INSTALL -eq 0 ]
then
  echo $CMD_ACTION
  if [ -n "${CMD_ACTION}" ]
  then

    if [ $DEBUG -eq 0 ]
    then
      sleep 1
      ${CMD_ACTION}
    fi

  fi
fi

exit 0
