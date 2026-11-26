import json
import os
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

# Palet Warna Modern Minimalist (Clean Dark UI dengan Aksen Indigo & Emerald)
BG_CANVAS = (0.06, 0.07, 0.10, 1)
SURFACE_CARD = (0.11, 0.13, 0.18, 1)
SURFACE_ELEVATED = (0.15, 0.18, 0.24, 1)
BORDER_SUBTLE = (0.22, 0.26, 0.35, 1)
ACCENT_PRIMARY = (0.38, 0.52, 0.98, 1)
ACCENT_SOFT = (0.38, 0.52, 0.98, 0.18)
EMERALD_OK = (0.18, 0.78, 0.56, 1)
CORAL_DANGER = (0.92, 0.34, 0.38, 1)
TEXT_HIGH = (0.97, 0.98, 1.0, 1)
TEXT_MEDIUM = (0.68, 0.73, 0.82, 1)
TEXT_LOW = (0.45, 0.50, 0.60, 1)

Window.clearcolor = BG_CANVAS


def request_android_permissions():
    """Meminta izin overlay (tampil di atas aplikasi lain) & wakelock di Android."""
    if platform != "android":
        return
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission

        request_permissions([
            Permission.WAKE_LOCK,
            Permission.FOREGROUND_SERVICE,
            Permission.POST_NOTIFICATIONS,
        ])

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        Intent = autoclass("android.content.Intent")

        activity = PythonActivity.mActivity
        if not Settings.canDrawOverlays(activity):
            intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:" + activity.getPackageName()),
            )
            activity.startActivity(intent)
    except Exception as e:
        print(f"[Mushi Permission Warning]: {e}")


class StyledCard(BoxLayout):
    """Kartu UI modern dengan sudut membulat dan garis tepi halus."""
    def __init__(self, bg_color=SURFACE_CARD, border_color=BORDER_SUBTLE, radius=16, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = [dp(radius)]
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
            if self.border_color:
                Color(*self.border_color)
                self.border_line = Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, dp(radius)),
                    width=1.1,
                )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if self.border_color:
            self.border_line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, self.radius[0]
            )


class RoundedButton(Button):
    """Tombol modern dengan sudut membulat bersih."""
    def __init__(self, btn_color=ACCENT_PRIMARY, text_color=(1, 1, 1, 1), radius=12, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.btn_color = btn_color
        self.radius = [dp(radius)]
        with self.canvas.before:
            self.color_inst = Color(*self.btn_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._on_state)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_state(self, instance, value):
        r, g, b, a = self.btn_color
        if value == "down":
            self.color_inst.rgba = (r * 0.8, g * 0.8, b * 0.8, a)
        else:
            self.color_inst.rgba = self.btn_color


class TimePickerModal(ModalView):
    """Pemilih Jam & Menit visual interaktif (tanpa perlu ketik titik dua manual)."""
    def __init__(self, initial_hour=12, initial_minute=0, on_confirm=None, **kwargs):
        super().__init__(size_hint=(0.86, 0.44), auto_dismiss=True, **kwargs)
        self.background_color = (0, 0, 0, 0.75)
        self.hour = initial_hour
        self.minute = initial_minute
        self.on_confirm = on_confirm

        card = StyledCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14),
            bg_color=SURFACE_ELEVATED,
            border_color=ACCENT_PRIMARY,
            radius=20,
        )

        title = Label(
            text="PILIH WAKTU KEGIATAN",
            font_size=dp(12),
            bold=True,
            color=ACCENT_PRIMARY,
            size_hint_y=None,
            height=dp(22),
        )
        card.add_widget(title)

        # Area Kontrol Jam : Menit
        picker_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(135))

        # Kolom Jam
        hour_col = BoxLayout(orientation="vertical", spacing=dp(6))
        btn_h_up = RoundedButton(text="+", font_size=dp(20), bold=True, btn_color=SURFACE_CARD, radius=10)
        btn_h_up.bind(on_release=lambda *_: self._change_hour(1))
        self.lbl_hour = Label(text=f"{self.hour:02d}", font_size=dp(34), bold=True, color=TEXT_HIGH)
        btn_h_down = RoundedButton(text="-", font_size=dp(20), bold=True, btn_color=SURFACE_CARD, radius=10)
        btn_h_down.bind(on_release=lambda *_: self._change_hour(-1))
        hour_col.add_widget(btn_h_up)
        hour_col.add_widget(self.lbl_hour)
        hour_col.add_widget(btn_h_down)

        sep = Label(text=":", font_size=dp(32), bold=True, color=ACCENT_PRIMARY, size_hint_x=None, width=dp(20))

        # Kolom Menit
        min_col = BoxLayout(orientation="vertical", spacing=dp(6))
        btn_m_up = RoundedButton(text="+", font_size=dp(20), bold=True, btn_color=SURFACE_CARD, radius=10)
        btn_m_up.bind(on_release=lambda *_: self._change_minute(5))
        self.lbl_min = Label(text=f"{self.minute:02d}", font_size=dp(34), bold=True, color=TEXT_HIGH)
        btn_m_down = RoundedButton(text="-", font_size=dp(20), bold=True, btn_color=SURFACE_CARD, radius=10)
        btn_m_down.bind(on_release=lambda *_: self._change_minute(-5))
        min_col.add_widget(btn_m_up)
        min_col.add_widget(self.lbl_min)
        min_col.add_widget(btn_m_down)

        picker_row.add_widget(hour_col)
        picker_row.add_widget(sep)
        picker_row.add_widget(min_col)
        card.add_widget(picker_row)

        # Shortcut menit presisi (+1 / -1)
        fine_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(32))
        btn_m_minus1 = RoundedButton(text="-1 Menit", font_size=dp(12), btn_color=SURFACE_CARD, radius=8)
        btn_m_minus1.bind(on_release=lambda *_: self._change_minute(-1))
        btn_m_plus1 = RoundedButton(text="+1 Menit", font_size=dp(12), btn_color=SURFACE_CARD, radius=8)
        btn_m_plus1.bind(on_release=lambda *_: self._change_minute(1))
        fine_row.add_widget(btn_m_minus1)
        fine_row.add_widget(btn_m_plus1)
        card.add_widget(fine_row)

        btn_save = RoundedButton(
            text="TERAPKAN JAM",
            font_size=dp(14),
            bold=True,
            btn_color=ACCENT_PRIMARY,
            radius=12,
            size_hint_y=None,
            height=dp(44),
        )
        btn_save.bind(on_release=self._confirm)
        card.add_widget(btn_save)

        self.add_widget(card)

    def _change_hour(self, delta):
        self.hour = (self.hour + delta) % 24
        self.lbl_hour.text = f"{self.hour:02d}"

    def _change_minute(self, delta):
        self.minute = (self.minute + delta) % 60
        self.lbl_min.text = f"{self.minute:02d}"

    def _confirm(self, *args):
        if self.on_confirm:
            self.on_confirm(f"{self.hour:02d}:{self.minute:02d}")
        self.dismiss()


class ForcedPopupModal(ModalView):
    """Pop-up paksa modern yang muncul saat jadwal tiba."""
    def __init__(self, task_title, task_time, on_dismiss_callback, **kwargs):
        super().__init__(size_hint=(0.88, 0.44), auto_dismiss=False, **kwargs)
        self.background_color = (0, 0, 0, 0.82)
        self.on_dismiss_callback = on_dismiss_callback

        container = StyledCard(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(14),
            bg_color=SURFACE_ELEVATED,
            border_color=EMERALD_OK,
            radius=22,
        )

        badge = Label(
            text="WAKTUNYA KEGIATAN DIMULAI",
            font_size=dp(12),
            bold=True,
            color=EMERALD_OK,
            size_hint_y=None,
            height=dp(22),
        )

        time_lbl = Label(
            text=task_time,
            font_size=dp(36),
            bold=True,
            color=TEXT_HIGH,
            size_hint_y=None,
            height=dp(46),
        )

        title_lbl = Label(
            text=task_title,
            font_size=dp(18),
            bold=True,
            color=TEXT_HIGH,
            halign="center",
            valign="middle",
        )
        title_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))

        done_btn = RoundedButton(
            text="SELESAI & TUTUP",
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(48),
            btn_color=EMERALD_OK,
            radius=14,
        )
        done_btn.bind(on_release=self._close_popup)

        container.add_widget(badge)
        container.add_widget(time_lbl)
        container.add_widget(title_lbl)
        container.add_widget(done_btn)
        self.add_widget(container)

    def _close_popup(self, *args):
        self.dismiss()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()


class MushiApp(App):
    def build(self):
        self.title = "Mushi - Asisten Jadwal"
        self.data_file = os.path.join(self.user_data_dir, "mushi_tasks.json")
        self.tasks = self.load_tasks()
        self.active_popup = None

        now = datetime.now()
        self.selected_time = now.strftime("%H:%M")

        root = BoxLayout(orientation="vertical", padding=[dp(18), dp(20), dp(18), dp(16)], spacing=dp(16))

        # 1. Top Header + Live Clock Badge
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(58))
        title_box = BoxLayout(orientation="vertical", spacing=dp(2))
        lbl_title = Label(
            text="Mushi",
            font_size=dp(26),
            bold=True,
            color=TEXT_HIGH,
            halign="left",
            valign="bottom",
        )
        lbl_title.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        lbl_sub = Label(
            text="Asisten Pengingat Pop-Up Otomatis",
            font_size=dp(12),
            color=TEXT_MEDIUM,
            halign="left",
            valign="top",
        )
        lbl_sub.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        title_box.add_widget(lbl_title)
        title_box.add_widget(lbl_sub)

        clock_card = StyledCard(
            orientation="vertical",
            bg_color=SURFACE_ELEVATED,
            border_color=BORDER_SUBTLE,
            radius=14,
            size_hint_x=None,
            width=dp(96),
            padding=[dp(8), dp(6)],
        )
        self.live_clock_lbl = Label(
            text=now.strftime("%H:%M"),
            font_size=dp(18),
            bold=True,
            color=ACCENT_PRIMARY,
        )
        live_tag = Label(text="SEKARANG", font_size=dp(9), bold=True, color=TEXT_LOW)
        clock_card.add_widget(self.live_clock_lbl)
        clock_card.add_widget(live_tag)

        top_bar.add_widget(title_box)
        top_bar.add_widget(clock_card)
        root.add_widget(top_bar)

        # 2. Card Input Kegiatan & Jam (Desain Bersih & Modern)
        form_card = StyledCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            bg_color=SURFACE_CARD,
            border_color=BORDER_SUBTLE,
            radius=18,
            size_hint_y=None,
            height=dp(215),
        )

        lbl_form_title = Label(
            text="TAMBAH KEGIATAN BARU",
            font_size=dp(11),
            bold=True,
            color=ACCENT_PRIMARY,
            halign="left",
            size_hint_y=None,
            height=dp(18),
        )
        lbl_form_title.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        form_card.add_widget(lbl_form_title)

        # Input Nama Kegiatan dengan wrapper bergaya modern
        input_wrapper = StyledCard(
            bg_color=SURFACE_ELEVATED,
            border_color=BORDER_SUBTLE,
            radius=12,
            padding=[dp(12), dp(4)],
            size_hint_y=None,
            height=dp(48),
        )
        self.input_task = TextInput(
            hint_text="Tulis nama kegiatan (misal: Belajar Etika Profesi)",
            multiline=False,
            font_size=dp(14),
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_HIGH,
            cursor_color=ACCENT_PRIMARY,
            hint_text_color=TEXT_LOW,
            padding=[0, dp(10)],
        )
        input_wrapper.add_widget(self.input_task)
        form_card.add_widget(input_wrapper)

        # Baris Pilih Jam + Tombol Simpan
        action_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(50))

        self.btn_pick_time = RoundedButton(
            text=f"Jam: {self.selected_time}",
            font_size=dp(15),
            bold=True,
            btn_color=SURFACE_ELEVATED,
            text_color=TEXT_HIGH,
            radius=12,
            size_hint_x=0.48,
        )
        self.btn_pick_time.bind(on_release=self.open_time_picker)

        btn_add = RoundedButton(
            text="+ Simpan Jadwal",
            font_size=dp(15),
            bold=True,
            btn_color=ACCENT_PRIMARY,
            text_color=(1, 1, 1, 1),
            radius=12,
            size_hint_x=0.52,
        )
        btn_add.bind(on_release=self.add_task)

        action_row.add_widget(self.btn_pick_time)
        action_row.add_widget(btn_add)
        form_card.add_widget(action_row)

        # Status Bar
        self.status_lbl = Label(
            text="Sistem aktif • Cek otomatis tiap 10 detik",
            font_size=dp(12),
            color=EMERALD_OK,
            halign="left",
            size_hint_y=None,
            height=dp(20),
        )
        self.status_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        form_card.add_widget(self.status_lbl)

        root.add_widget(form_card)

        # 3. Header Daftar Kegiatan
        list_header_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        list_header = Label(
            text="JADWAL KEGIATAN KAMU",
            font_size=dp(12),
            bold=True,
            color=TEXT_MEDIUM,
            halign="left",
        )
        list_header.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        self.count_lbl = Label(
            text="0 Agenda",
            font_size=dp(12),
            color=TEXT_LOW,
            halign="right",
        )
        self.count_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        list_header_row.add_widget(list_header)
        list_header_row.add_widget(self.count_lbl)
        root.add_widget(list_header_row)

        # 4. ScrollView Daftar Kartu Kegiatan
        scroll = ScrollView(bar_width=dp(3), bar_color=ACCENT_PRIMARY)
        self.task_list_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter("height"))
        scroll.add_widget(self.task_list_layout)
        root.add_widget(scroll)

        self.refresh_task_list()

        # Interval pengecekan 10 detik (hemat CPU & baterai)
        Clock.schedule_interval(self.check_schedules, 10)
        return root

    def open_time_picker(self, *args):
        h, m = map(int, self.selected_time.split(":"))
        picker = TimePickerModal(initial_hour=h, initial_minute=m, on_confirm=self.on_time_selected)
        picker.open()

    def on_time_selected(self, time_str):
        self.selected_time = time_str
        self.btn_pick_time.text = f"Jam: {self.selected_time}"

    def on_start(self):
        request_android_permissions()
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                service = autoclass("org.mushi.mushi.ServiceMushiservice")
                service.start(PythonActivity.mActivity, "")
            except Exception as e:
                print(f"[Mushi Service Info]: {e}")

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_tasks(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, *args):
        title = self.input_task.text.strip()
        target_time = self.selected_time

        if not title:
            self.status_lbl.text = "Isi nama kegiatan terlebih dahulu!"
            self.status_lbl.color = CORAL_DANGER
            return

        self.tasks.append({
            "id": int(datetime.now().timestamp() * 1000),
            "title": title,
            "time": target_time,
            "triggered_date": "",
        })
        self.save_tasks()
        self.input_task.text = ""
        self.status_lbl.text = f"Tersimpan: '{title}' pada pukul {target_time}"
        self.status_lbl.color = EMERALD_OK
        self.refresh_task_list()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()
        self.refresh_task_list()

    def refresh_task_list(self):
        self.task_list_layout.clear_widgets()
        self.count_lbl.text = f"{len(self.tasks)} Agenda"

        if not self.tasks:
            empty_card = StyledCard(
                orientation="vertical",
                bg_color=SURFACE_CARD,
                border_color=BORDER_SUBTLE,
                radius=16,
                padding=dp(20),
                size_hint_y=None,
                height=dp(90),
            )
            empty_title = Label(
                text="Belum ada jadwal kegiatan",
                font_size=dp(14),
                bold=True,
                color=TEXT_MEDIUM,
            )
            empty_sub = Label(
                text="Masukkan kegiatan & pilih jam di atas untuk mulai",
                font_size=dp(12),
                color=TEXT_LOW,
            )
            empty_card.add_widget(empty_title)
            empty_card.add_widget(empty_sub)
            self.task_list_layout.add_widget(empty_card)
            return

        today_str = datetime.now().strftime("%Y-%m-%d")
        for task in sorted(self.tasks, key=lambda x: x["time"]):
            is_done = task.get("triggered_date") == today_str
            card = StyledCard(
                orientation="horizontal",
                padding=[dp(14), dp(12)],
                spacing=dp(12),
                bg_color=SURFACE_CARD,
                border_color=EMERALD_OK if is_done else BORDER_SUBTLE,
                radius=16,
                size_hint_y=None,
                height=dp(72),
            )

            # Badge Jam di sebelah kiri
            time_pill = StyledCard(
                orientation="vertical",
                bg_color=ACCENT_SOFT,
                border_color=None,
                radius=12,
                size_hint_x=None,
                width=dp(74),
            )
            lbl_t = Label(
                text=task["time"],
                font_size=dp(17),
                bold=True,
                color=ACCENT_PRIMARY,
            )
            time_pill.add_widget(lbl_t)

            # Detail Kegiatan di tengah
            info = BoxLayout(orientation="vertical", spacing=dp(2))
            lbl_n = Label(
                text=task["title"],
                font_size=dp(15),
                bold=True,
                color=TEXT_HIGH,
                halign="left",
                valign="bottom",
            )
            lbl_n.bind(size=lambda inst, val: setattr(inst, "text_size", val))

            status_txt = "Sudah diingatkan hari ini" if is_done else "Menunggu jadwal..."
            lbl_s = Label(
                text=status_txt,
                font_size=dp(11),
                color=EMERALD_OK if is_done else TEXT_LOW,
                halign="left",
                valign="top",
            )
            lbl_s.bind(size=lambda inst, val: setattr(inst, "text_size", val))

            info.add_widget(lbl_n)
            info.add_widget(lbl_s)

            # Tombol Hapus di kanan
            btn_del = RoundedButton(
                text="Hapus",
                font_size=dp(12),
                bold=True,
                size_hint_x=None,
                width=dp(68),
                btn_color=CORAL_DANGER,
                radius=10,
            )
            btn_del.bind(on_release=lambda inst, tid=task["id"]: self.delete_task(tid))

            card.add_widget(time_pill)
            card.add_widget(info)
            card.add_widget(btn_del)
            self.task_list_layout.add_widget(card)

    def check_schedules(self, dt):
        now = datetime.now()
        current_hm = now.strftime("%H:%M")
        today_str = now.strftime("%Y-%m-%d")
        self.live_clock_lbl.text = current_hm

        for task in self.tasks:
            if task["time"] == current_hm and task.get("triggered_date") != today_str:
                if self.active_popup is None:
                    task["triggered_date"] = today_str
                    self.save_tasks()
                    self.refresh_task_list()
                    self.trigger_forced_popup(task["title"], task["time"])
                    break

    def trigger_forced_popup(self, title, time_str):
        def on_closed():
            self.active_popup = None

        self.active_popup = ForcedPopupModal(title, time_str, on_closed)
        self.active_popup.open()


if __name__ == "__main__":
    MushiApp().run()
