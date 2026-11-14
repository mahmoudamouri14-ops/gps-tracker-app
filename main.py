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

class GPSTrackerApp(App):
    def build(self):
        self.title = "GPS Tracker"
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # الحالة العامة
        self.status_label = Label(text="الحالة: متوقف", font_size=18, size_hint_y=None, height=40)
        layout.add_widget(self.status_label)
        
        # عرض الإحداثيات الحالية
        self.coord_label = Label(text="خط العرض: 0.0 | خط الطول: 0.0", font_size=18, size_hint_y=None, height=40)
        layout.add_widget(self.coord_label)
        
        # رابط السيرفر السحابي (جاهز برابط قاعدة بياناتك)
        layout.add_widget(Label(text="رابط السيرفر السحابي (Cloud URL):", size_hint_y=None, height=25))
        self.url_input = TextInput(
            text="https://livetrackerapp-66257-default-rtdb.europe-west1.firebasedatabase.app/location.json",
            size_hint_y=None, height=45, multiline=False
        )
        layout.add_widget(self.url_input)
        
        # معرف الجوال
        layout.add_widget(Label(text="اسم أو رقم هذا الجوال:", size_hint_y=None, height=25))
        self.device_input = TextInput(
            text="phone_1",
            size_hint_y=None, height=45, multiline=False
        )
        layout.add_widget(self.device_input)
        
        # زر البدء والإيقاف
        self.toggle_btn = Button(text="بدء التتبع والإرسال", font_size=20, size_hint_y=None, height=60)
        self.toggle_btn.bind(on_press=self.toggle_tracking)
        layout.add_widget(self.toggle_btn)
        
        # حالة المزامنة السحابية
        self.sync_label = Label(text="السيرفر: بانتظار الإرسال...", font_size=16, size_hint_y=None, height=40)
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
        
        # تحديث الواجهة عبر مسار الرئيسي لـ Kivy
        Clock.schedule_once(lambda dt: self.update_ui_coords(self.lat, self.lon))
        
        # إرسال الإحداثيات للسيرفر في الخلفية لكي لا يجمد التطبيق
        t = threading.Thread(target=self.send_to_cloud, args=(self.lat, self.lon))
        t.daemon = True
        t.start()

    def update_ui_coords(self, lat, lon):
        self.coord_label.text = f"خط العرض: {lat:.5f} | خط الطول: {lon:.5f}"

    def on_gps_status(self, convening, status):
        pass

    def send_to_cloud(self, lat, lon):
        try:
            base_url = self.url_input.text.strip()
            device_id = self.device_input.text.strip()
            if not base_url or "your-database-name" in base_url:
                Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', 'خطأ: يرجى وضع رابط سيرفر حقيقي'))
                return
            
            payload = {
                "device": device_id,
                "lat": lat,
                "lon": lon,
                "time": time.time()
            }
            
            # إرسال البيانات عبر طلب PUT لسيرفر سحابي مجاني مثل Firebase
            response = requests.put(base_url, json=payload, timeout=5)
            if response.status_code == 200 or response.status_code == 204:
                Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', 'السيرفر: تم إرسال الإحداثيات بنجاح ✅'))
            else:
                Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', f'السيرفر: خطأ بالاتصال ({response.status_code})'))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.sync_label, 'text', 'السيرفر: فشل الاتصال بالإنترنت ❌'))

if __name__ == '__main__':
    GPSTrackerApp().run()
