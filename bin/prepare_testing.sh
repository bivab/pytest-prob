#!/bin/sh
os=`uname`

case $os in

Darwin)
    echo "Running on OS X"
    url="http://nightly.cobra.cs.uni-duesseldorf.de/tcl/ProB.mac_os.10.7.5.x86_64.tar.gz"
    ;;

Linux)
    echo "Running on Linux"
    wordsize=`uname -m`
    if [ $wordsize = "x86_64" ]
    then
      echo "64 bit"
      url="http://nightly.cobra.cs.uni-duesseldorf.de/tcl/ProB.linux64.tar.gz"
    else
      echo "32 bit"
      url="http://nightly.cobra.cs.uni-duesseldorf.de/tcl/ProB.linux32.tar.gz"
    fi
    ;;

*)
    >&2 echo "Failure: Unsupported OS '${os}'"
    exit 1
    ;;
esac

echo "curl ${url} -z download.tar.gz -o download.tar.gz"
curl ${url} -z download.tar.gz -o download.tar.gz
mkdir prob
tar -xvf download.tar.gz -C prob --strip-components 1
