
#!/bin/bash
set -e

export PYTHONWARNINGS="ignore"

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

VENV=".venv"


# activate_virtual_env
function activate_virtual_env() {
    # Create virtualenv

     # Python 3.11.7 with Window
    if [ -d "$VENV/bin" ]; then
        source $SCRIPTDIR/$VENV/bin/activate
        echo "Sourced virtual enviroment >>" + $SCRIPTDIR/$VENV/bin/activate
    else
        source $SCRIPTDIR/$VENV/Scripts/activate
        echo "Sourced virtual enviroment >>" + $SCRIPTDIR/$VENV/Scripts/activate
    fi

}

activate_virtual_env
echo $SCRIPTDIR

# Curtator Test
curator --dry-run /home/user/utils/curator-config-dev/delete.yml --config /home/user/utils/curator-config-dev/config-3.yml

deactivate