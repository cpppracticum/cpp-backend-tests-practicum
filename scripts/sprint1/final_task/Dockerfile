FROM gcc:12.5 AS build

RUN apt update && \
    apt install -y \
      python3-pip \
      cmake \
      python3-venv

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir conan==1.*

COPY conanfile.txt /app/
RUN mkdir /app/build && cd /app/build && \
    conan install .. --build=missing

COPY ./src /app/src
COPY CMakeLists.txt /app/

RUN cd /app/build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build .

FROM ubuntu:24.04 AS run

RUN groupadd -r www && useradd -r -g www www
USER www

COPY --from=build /app/build/bin/game_server /app/
COPY ./data /app/data

ENTRYPOINT ["/app/game_server", "/app/data/config.json"]
