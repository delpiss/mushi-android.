[app]

title = Mushi
package.name = mushi
package.domain = org.mushi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

requirements = python3,kivy==2.3.0,pyjnius
services = Mushiservice:service.py:foreground

orientation = portrait
fullscreen = 0
# icon.filename = %(source.dir)s/icon.png

android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = WAKE_LOCK,FOREGROUND_SERVICE,SYSTEM_ALERT_WINDOW,POST_NOTIFICATIONS,RECEIVE_BOOT_COMPLETED
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
