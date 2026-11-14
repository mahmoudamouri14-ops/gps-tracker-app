import threading
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from plyer import gps
import requests

# رابط السيرفر السحابي الخاص بك مثبت في الخلفية لضمان نظافة واجهة الجوال
FIREBASE_URL = "https://livetrackerapp-66257-default-rtdb.europe-west1.firebasedatabase.app/location.json"

class GPSTrackerApp(App):
    def build(self):
        self.title = "GPS Tracker"
        # تصميم الواجهة بمسافات مرتبة ومريحة للعين على الجوال
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # عنوان التطبيق في الأعلى
        layout.add_widget(Label(text="نظام تتبع الموقع اللحظي", font_size=20, size_hint_y=None, height=40, bold=True))
        
        # الحالة العامة
        self.status_label = Label(text="الحالة: متوقف", font_size=18, size_hint_y=None, height=40)
        layout.add_widget(self.status_label)
        
        # عرض الإحداثيات الحالية بوضوح
        self.coord_label = Label(text="خط العرض: 0.0\nخط الطول: 0.0", font_size=16, size_hint_y=None, height=60)
        layout.add_widget(self.coord_label)
        
        # معرف الجوال (لتعريف الجهاز المرسل)
        layout.add_widget(Label(text="اسم هذا الجوال:", size_hint_y=None, height=25))
        self.device_input = TextInput(
            text="phone_1",
            size_hint_y=None, height=45, multiline=False, font_size=16
        )
        layout.add_widget(self.device_input)
        
        # زر البدء والإيقاف بتصميم كبير وواضح
        self.toggle_btn = Button(text="بدء التتبع والإرسال", font_size=18, size_hint_y=None, height=60)
        self.toggle_btn.bind(on_press=self.toggle_tracking)
        layout.add_widget(self.toggle_btn)
        
        # حالة المزامنة السحابية
        self.sync_label = Label(text="السيرفر: بانتظار الإرسال...", font_size=15, size_hint_y=None, height=40)
        layout.add_widget(self.sync_label)
        
        self.tracking = False
        self.lat = 0.0
        self.lon = 0.0
        
        return layout

    def toggle_tracking(self, instance):
        if not self.tracking:
            self.start_gps()
            self.tracking = True
            self.toggle_btn.text = "إيقاف التتبع"
            self.status_label.text = "الحالة: جاري التتبع والإرسال..."
        else:
            self.stop_gps()
            self.tracking = False
            self.toggle_btn.text = "بدء التتبع والإرسال"
            self.status_label.text = "الحالة: متوقف"
            self.sync_label.text = "السيرفر: متوقف"

    def start_gps(self):
        try:
            gps.configure(on_location=self.on_gps_location, on_status=self.on_gps_status)
            gps.start(min_time=5000, min_distance=1)
            self.status_label.text = "الحالة: تم تشغيل الـ GPS"
        except NotImplementedError:
            self.status_label.text = "الحالة: الـ GPS غير مدعوم على هذا الجهاز"

    def stop_gps(self):
        try:
            gps.stop()
        except:
            pass

    def on_gps_location(self, **kwargs):
        self.lat = kwargs.get('lat', 0.0)
        self.lon = kwargs.get('lon', 0.0)
        
        # تحديث الواجهة بأمان
        Clock.schedule_once(lambda dt: self.update_ui_coords(self.lat, self.lon))
        
        # إرسال الإحداثيات للسيرفر في الخلفية
        t = threading.Thread(target=self.send_to_cloud, args=(self.lat, self.lon))
        t.daemon = True
        t.start()

    def update_ui_coords(self, lat, lon):
        self.coord_label.text = f"خط العرض: {lat:.5f}\nخط الطول: {lon:.5f}"

    def on_gps_status(self, convening, status):
        pass

    def send_to_cloud(self, lat, lon):
        try:
            device_id = self.device_input.text.strip()
            payload = {
                "device": device_id,
                "lat": lat,
                "lon": lon,
                "time": time.time()
            }
            
            # إرسال البيانات مباشرة لرابط فايربيس المثبت في الخلفية
            response = requests.put(FIREBASE_URL, json=payload, timeout=5)
            if response.status_code == 200 or response.status_code == 204:
                Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', 'السيرفر: تم إرسال الإحداثيات بنجاح ✅'))
            else:
                Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', f'السيرفر: خطأ بالاتصال ({response.status_code})'))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', 'السيرفر: فشل الاتصال بالإنترنت ❌'))

if __name__ == '__main__':
    GPSTrackerApp().run()
