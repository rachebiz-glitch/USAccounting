[app]
title = USAccountingApp
package.name = usaccounting
package.domain = org.vargas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Keep requirements short for the first build
requirements = python3, kivy==2.3.0, hostpython3, pyjnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.api = 34
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
