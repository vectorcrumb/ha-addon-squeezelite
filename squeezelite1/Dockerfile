# Home Assistant overrides BUILD_FROM with the architecture-specific build.json pin.
ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base@sha256:6e7ef11cacd4c36c98a7f38e621b170398a79df4f77c31729cfaf2161774c094
FROM ${BUILD_FROM} AS base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get upgrade -y -o Dpkg::Options::="--force-confold" \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
# Includes the October 2026 Ogg bounds and malformed-MP4 fixes.
ARG SL_COMMIT=cc7ee7c0d00bd2aa691a574a7d429d5cd13c858b
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential ca-certificates git libpulse-dev libflac-dev \
        libvorbis-dev libmpg123-dev libfaad-dev libopusfile-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN git init /src \
    && git -C /src remote add origin https://github.com/ralph-irving/squeezelite.git \
    && git -C /src fetch --depth 1 origin "${SL_COMMIT}" \
    && git -C /src checkout --detach FETCH_HEAD \
    && test "$(git -C /src rev-parse HEAD)" = "${SL_COMMIT}"
RUN make -C /src -f Makefile.pulse \
        OPTS="-DPULSEAUDIO -DLINKALL -DUSE_SSL -DOPUS -DNO_MAD" \
        CFLAGS="-Wall -fPIC -O2 -fcommon -std=gnu99 -fstack-protector-strong -D_FORTIFY_SOURCE=2" \
        CPPFLAGS="-I/usr/include/opus" \
        LDFLAGS="-Wl,-z,relro,-z,now,-z,noexecstack" \
    && strip /src/squeezelite-pulse

FROM base
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates libpulse0 libflac14 libvorbisfile3 libmpg123-0t64 \
        libfaad2 libopusfile0 libssl3t64 \
    && rm -rf /var/lib/apt/lists/*
# The inherited template renderer is unused and carries separately bundled Go dependencies.
RUN rm -f /usr/bin/tempio
COPY --from=builder /src/squeezelite-pulse /usr/local/bin/squeezelite
COPY rootfs /
ARG BUILD_ARCH
ARG BUILD_VERSION
LABEL io.hass.name="Squeezelite" \
      io.hass.type="addon" \
      io.hass.arch="${BUILD_ARCH}" \
      io.hass.version="${BUILD_VERSION}" \
      org.opencontainers.image.source="https://github.com/vectorcrumb/ha-addon-squeezelite" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"
