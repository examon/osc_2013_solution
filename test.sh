#!/bin/bash
# Tomas Meszaros <exo@tty.sk>
# test.sh

# Automated testing scenario for https://bugzilla.redhat.com/show_bug.cgi?id=1020191
# 1. Check if condor-aviary is installed.
# 2. [optional] Clear all /var/lib/condor/spool/* so we will have clear job list.
# 3. Submit 10 jobs using aviary/submit.py.
# 4. Check if is table correctly sorted.

# Usage: ./test.sh

# Change this if the check_cumin_submission script is named
# differently or in the different folder
CHECK_SUBMISSIONS_SCRIPT="check_cumin_submissions.py"

check_aviary() {
  echo -e "=> checking condor-aviary... (this may take a while)"
  aviary_rpm=condor-aviary
  if rpm -qa | grep -q $aviary_rpm; then
    echo "*OK* $aviary_rpm installed"
  else
    echo "*ERROR* missing $aviary_rpm package! Aborting."
    exit
  fi
}

clear_submissions() {
  echo -e "\n=> [You can skip this] Do you want to clear submissions table? [y/N] "
  read x

  if [[ $x == "y" || $x == "Y" ]]; then
    check_if_running condor 0
    check_if_running cumin-data 0
    check_if_running cumin-web 0
    echo -e "\n=> [root] removing /var/lib/condor/spool/*"
    su -c "rm -rf /var/lib/condor/spool/*"
    echo "*DONE* /var/lib/condor/spool/* removed"
    echo "Please restart cumin and condor in order to proceed. Aborting."
    exit
  fi
}

submit_jobs() {
  check_if_running condor 1
  check_if_running cumin-data 1
  check_if_running cumin-web 1

  export PYTHONPATH=/usr/share/condor/aviary/module
  echo -e "\n=> Submitting 10 jobs..."
  for i in {1..10}
    do
      /usr/share/condor/aviary/submit.py
    done
}

check_if_running() {
  if [[ $1 == "condor" ]]; then
    pid=$(pgrep --oldest $1)
  else
    pid=$(ps -a | grep $1 | awk '{print $1}')
  fi

  if [ $2 == 1 ] && [ -z $pid ]; then
    echo -e "\n=> $1 is not running. Please start $1 and run this script again. Aborting."
    exit
  fi

  if [ $2 == 0 ] && [[ $pid =~ ^-?[0-9]+$ ]]; then
    echo -e "\n=> $1 is running. Please stop $1 and run this script again. Aborting."
    exit
  fi
}

check_table() {
  echo -en "\n=> Please enter your cumin username: "
  read cumin_username
  echo -en "\n=> Please enter your cumin passowrd: "
  read -s cumin_password
  echo -e "\nPlease wait. Loading..."

  if ! python $CHECK_SUBMISSIONS_SCRIPT $cumin_username $cumin_password; then
    echo -e "\n*FAILED* Table is not sorted correctly!"
    exit
  else
    echo -e "\n*PASSED* Table is sorted correctly!"
    exit
  fi
  echo -e "\n*ERROR* Something bad happened!"
}

# Run the stuff
check_aviary
clear_submissions
submit_jobs
check_table
