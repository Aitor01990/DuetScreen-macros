#!/usr/bin/env bash
set -euo pipefail
target="$1"
assets="${DUETSCREEN_SRC:?}/assets/indart3d"
install -m644 "$assets/distribution.json" "$target/etc/indart3d-release.json"
if [ -f "$assets/splash_0.png" ]; then
    install -d "$target/etc/splash"
    install -m644 "$assets/splash_0.png" "$target/etc/splash/splash_0.png"
    install -m644 "$assets/splash_0.png" "$target/etc/splash.png"
fi
