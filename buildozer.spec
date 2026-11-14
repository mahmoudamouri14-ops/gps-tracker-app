[app]
title = GPSTracker
package.name = gpstracker
package.domain = org.tracker
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 1.0
requirements = python3,kivy,plyer,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 1
warn_on_root = 1
