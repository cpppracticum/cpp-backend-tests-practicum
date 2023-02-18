FROM gcc:11.3

RUN apt update && \
    apt install -y \
      python3-pip \
      cmake \
    && \
    pip3 install conan

COPY solution /app
WORKDIR /app

RUN mkdir -p /app/build

RUN cd build && \
    conan install .. --build=missing -s compiler.libcxx=libstdc++11 -s build_type=Release

RUN cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . -j $(nproc)

RUN cp build/bin/game_server game_server


ENTRYPOINT ["/app/game_server",  "/app/data/config.json", "/app/static"]
