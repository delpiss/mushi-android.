import json
import os
import time
from datetime import datetime
from jnius import autoclass


def run_background_monitor():
    """Background service Android untuk memantau jadwal tiap 10 detik."""
    PythonService = autoclass("org.kivy.android.PythonService")
    Context = autoclass("android.content.Context")
    Intent = autoclass("android.content.Intent")
    PowerManager = autoclass("android.os.PowerManager")

    service = PythonService.mService
    service.setAutoRestartService(True)

    pm = service.getSystemService(Context.POWER_SERVICE)
    wake_lock = pm.newWakeLock(
        PowerManager.PARTIAL_WAKE_LOCK,
        "Mushi::ScheduleMonitorLock"
    )
    wake_lock.acquire()

    data_path = os.path.join(service.getFilesDir().getAbsolutePath(), "app", "mushi_tasks.json")
    alt_path = os.path.join(service.getFilesDir().getAbsolutePath(), "mushi_tasks.json")

    while True:
        try:
            target_file = data_path if os.path.exists(data_path) else alt_path
            if os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as f:
                    tasks = json.load(f)

                now = datetime.now()
                current_hm = now.strftime("%H:%M")
                today_str = now.strftime("%Y-%m-%d")

                for task in tasks:
                    if task.get("time") == current_hm and task.get("triggered_date") != today_str:
                        pm_pkg = service.getPackageManager()
                        launch_intent = pm_pkg.getLaunchIntentForPackage(service.getPackageName())
                        if launch_intent is not None:
                            launch_intent.addFlags(
                                Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
                            )
                            service.startActivity(launch_intent)
                        break
        except Exception as e:
            print(f"[Mushi Background Service Error]: {e}")

        time.sleep(10)


if __name__ == "__main__":
    run_background_monitor()
