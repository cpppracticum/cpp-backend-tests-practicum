REPO=${PWD}

APPDIR=${REPO}/sprint1/problems/final_task/solution

printf "#!/bin/sh\ndocker run --rm -p 8080:8080 my_http_server" > ${APPDIR}/run_docker.sh
chmod +x ${APPDIR}/run_docker.sh

source ${REPO}/.venv/bin/activate

export DELIVERY_APP=${APPDIR}/run_docker.sh

python3 -m pytest --rootdir=${REPO} --verbose --junitxml=results.xml cpp-backend-tests-practicum/tests/test_l05_final_task.py

rm ${APPDIR}/run_docker.sh