#!/bin/bash -e

# Container entrypoint to simplify running the production and dev servers.

# Entrypoint conventions are as follows:
#
#  -  If the container is run without a custom CMD, the service should run as it would in production.
#  -  If the container is run with the "dev" CMD, the service should run in development mode.
#
#     Normally, this means that if the user's source has been mounted as a volume, the server will
#     restart on code changes and will inject extra debugging/diagnostics.
#
#  -  If the CMD is "test" or "lint", the service should run its unit tests or linting.
#
#     There is no requirement that unit tests work unless user source has been mounted as a volume;
#     test code should not normally be shipped with production images.
#
#  -  Otherwise, the CMD should be run verbatim.


if [ "$1" = "test" ]; then
   # Install standard test dependencies; YMMV
   pip --quiet install \
       .[test] nose PyHamcrest coverage

   apt-get update && apt-get install netcat -y
   echo "Waiting for Elasticsearch to start on 9200..."
   while ! netcat -z elasticsearch 9200; do
     echo "Elasticsearch not up, sleeping for 1s"
     sleep 1
   done
   echo "Elasticsearch launched"

   exec nosetests
elif [ "$1" = "lint" ]; then
   # Install standard linting dependencies; YMMV
   pip --quiet install \
       .[lint] flake8 flake8-print flake8-logging-format flake8-isort
   flake8 ${NAME}
elif [ "$1" = "typehinting" ]; then
   # Install standard type-linting dependencies
   pip --quiet install mypy
   mypy ${NAME} --ignore-missing-imports
else
   echo "Cannot execute $@"
   exit 3
fi
