[app]
title = USAccounting
package.name = usaccounting
package.domain = org.vargas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy==2.3.0
orientation = portrait
android.archs = arm64-v8a
android.api = 31
android.minapi = 21
android.ndk = 25b
# Removing the explicit 'android.sdk' line to let Buildozer auto-select the best one
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
