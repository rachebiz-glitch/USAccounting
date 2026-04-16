[app]
# (str) Title of your application
title = My App

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# DO NOT include built-ins like os, random, or math here!
requirements = python3,kivy==2.3.0,pillow

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# =============================================================================
# Android specific
# =============================================================================

# (int) Target Android API, should be as high as possible.
# Use 33 or 34 for modern Google Play requirements
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use. Version 25b/25c is the most stable for Kivy.
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK API to use. Usually matches android.minapi.
android.ndk_api = 21

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk
