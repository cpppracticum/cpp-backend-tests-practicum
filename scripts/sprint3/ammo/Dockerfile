from praktikumcpp/practicum_cpp_backend_server:latest

COPY solution /solution
COPY tests/test_s03_ammo.py /test_s03_ammo.py


# run echo "docker run --rm -p 8080:8080 -d praktikumcpp/game_server:latest" >> run.sh
run echo "yandex-tank -c /solution/load.yaml /solution/ammo.txt" >> run.sh
run echo "echo Next stage" >> run.sh
run echo "pytest --junitxml=/ammo.xml /test_s03_ammo.py" >> run.sh
CMD bash run.sh
