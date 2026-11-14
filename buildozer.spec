[app]

# (str) Title of your application
title = GPS Tracker

# (str) Package name
package.name = gpstracker

# (str) Package domain (needed for android packaging)
package.domain = org.gps

# (str) Source files to include (let it include python files and assets)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# تأكد أن مكتبات الـ GPS والإنترنت موجودة هنا
requirements = python3,kivy,plyer,requests,urllib3,idna,certifi,charset_normalizer

# (str) Supported orientations
orientation = portrait

# (list) Permissions
# صلاحيات الإنترنت والموقع الجغرافي الضرورية للـ GPS
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Indicate whether the application is a game or not
osx.python_version = 3
osx.kivy_version = 1.9.1

[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = .buildozer

# (str) Path to build output (PKGs)
bin_dir = bin
