FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN sudo apt update && \
    sudo apt-get install -y \
    ffmpeg \
    libunistring-dev \
    libaom-dev \
    libdav1d-dev \
    autoconf \
    automake \
    build-essential \
    cmake \
    git-core \
    libass-dev \
    libfreetype6-dev \
    libgnutls28-dev \
    libmp3lame-dev \
    libsdl2-dev \
    libtool \
    libva-dev \
    libvdpau-dev \
    libvorbis-dev \
    libxcb1-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    meson \
    ninja-build \
    pkg-config \
    texinfo \
    wget \
    yasm \
    zlib1g-dev \
    doxygen \
    git \
    graphviz \
    imagemagick \
    libasound2-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libgmp-dev \
    libopencore-amrnb-dev \
    libopencore-amrwb-dev \
    libopus-dev \
    librtmp-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-net-dev \
    libsdl2-ttf-dev \
    libsnappy-dev \
    libsoxr-dev \
    libssh-dev \
    libssl-dev \
    libv4l-dev \
    libvo-amrwbenc-dev \
    libwebp-dev \
    libx264-dev \
    libx265-dev \
    libxcb-shape0-dev \
    libxml2-dev \
    lzma-dev \
    python3-dev \
    python3-pip \
    libdrm-dev

RUN pip install --upgrade pip

RUN mkdir -p /src \
    && git clone --branch release/6.0 --depth 1 https://github.com/FFmpeg/FFmpeg.git /src/FFmpeg

RUN cd /src/FFmpeg \
    && ./configure \
    --extra-cflags="-I/usr/local/include" \
    --extra-ldflags="-L/usr/local/lib" \
    --extra-libs="-lpthread -lm -latomic" \
    --ld="g++" \
    --bindir="$HOME/bin" \
    --enable-gpl \
    --enable-libaom \
    --enable-libass \
    --enable-libfreetype \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-libvorbis \
    --enable-libx264 \
    --enable-libx265 \
    --enable-nonfree \
    --enable-gmp \
    --enable-libdrm \
    --enable-libopencore-amrnb \
    --enable-libopencore-amrwb \
    --enable-librtmp \
    --enable-libsnappy \
    --enable-libsoxr \
    --enable-libssh \
    --enable-libwebp \
    --enable-libxml2 \
    --enable-version3 \
    --target-os=linux \
    --enable-pthreads \
    --enable-openssl \
    --enable-hardcoded-tables \
    --enable-pic \
    --disable-static \
    --enable-shared

RUN cd /src/FFmpeg \
    && make -j$(nproc)

RUN cd /src/FFmpeg \
    && sudo make install

RUN cd /src/FFmpeg \
    && sudo ldconfig
