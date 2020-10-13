#!/bin/sh
# Create a directory for the output
mkdir -p output
# Execute docker with appropriate flags while passing in any arguments.
# --rm removes the container after execution
# -it makes the container interactive (particularly useful with --debug)
# -v mounts volumes for cache, output, and copies in the local settings

LOAD_DATA="docker run --rm -it -e REGS_GOV_KEY='$1' --network host -v eregs-cache:/app/cache -v $PWD/output:/app/output -v $PWD/config/regulations-parser/local_settings.py:/app/src/local_settings.py eregs_parser_kaitlin ${@:2}"

# Check to see if terminal is tty. If not do not run the -it command in docker.
if tty -s;
then
  $LOAD_DATA
else
  winpty $LOAD_DATA
fi
