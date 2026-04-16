[app]
title = USAccounting
package.name = usaccounting
package.domain = org.vargas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Using specific versions to force a clean environment
requirements = python3==3.10.12, hostpython3==3.10.12, kivy==2.3.0

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

