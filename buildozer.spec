[app]
title = USAccounting
package.name = usaccounting
package.domain = org.vargas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Fixed requirements to avoid the 'NoneType' crash
requirements = python3,kivy==2.3.0,hostpython3

orientation = portrait
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
