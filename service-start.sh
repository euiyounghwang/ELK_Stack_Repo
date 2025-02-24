

#!/bin/bash
set -e

# Activate virtualenv && run serivce

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTDIR

VENV="rest_api/.venv"

# Python 3.11.7 with Window
if [ -d "$VENV/bin" ]; then
    source $VENV/bin/activate
else
    source $VENV/Scripts/activate
fi

cd $SCRIPTDIR/rest_api

python -m uvicorn main:app --reload --host=0.0.0.0 --port=9001 --workers 1
# gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:9001 --workers 4
# poetry run uvicorn main:app --reload --host=0.0.0.0 --port=9001 --workers 4
