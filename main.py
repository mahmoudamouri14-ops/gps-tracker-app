from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from plyer import gps
import requests

# ** استبدل هذا الرابط برابط سيرفرك السحابي الحقيقي لاحقاً **
SERVER_URL = "https://your-app-name.onrender.com"

class TrackerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        self.label = Label(text="اختر وضع التشغيل لتطبيق التتبع", font_size=18)
        self.layout.add_widget(self.label)
        
        btn_send = Button(text="📡 أنا الجوال المرسل (إرسال موقعي)", background_color=(0, 0.7, 0, 1), font_size=16)
        btn_send.bind(on_press=self.start_sending)
        self.layout.add_widget(btn_send)
        
        btn_watch = Button(text="🗺️ أنا الجوال المستقبل (مراقبة الموقع)", background_color=(0, 0.4, 0.8, 1), font_size=16)
        btn_watch.bind(on_press=self.start_watching)
        self.layout.add_widget(btn_watch)
        
        return self.layout

    def start_sending(self, instance):
        self.label.text = "جاري تفعيل الـ GPS وإرسال الموقع للسحابة..."
        try:
            gps.configure(on_location=self.on_gps_location)
            gps.start(minTime=1000, minDistance=1)
        except Exception:
            self.label.text = "خطأ في تشغيل الـ GPS."

    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            try:
                requests.post(f"{SERVER_URL}/update", json={'lat': lat, 'lon': lon}, timeout=5)
                self.label.text = f"تم الإرسال للسحابة:\nLat: {lat:.4f}\nLon: {lon:.4f}"
            except Exception:
                self.label.text = "فشل الاتصال بالسيرفر السحابي للإرسال."

    def start_watching(self, instance):
        self.label.text = "جاري الاتصال بالسحابة لمراقبة الموقع..."
        Clock.schedule_interval(self.fetch_location_from_cloud, 3)

    def fetch_location_from_cloud(self, dt):
        try:
            response = requests.get(f"{SERVER_URL}/get", timeout=5)
            if response.status_code == 200:
                data = response.json()
                lat = data.get('lat')
                lon = data.get('lon')
                self.label.text = f"📍 موقع الجوال المرسل المستلم:\nLat: {lat}\nLon: {lon}"
            else:
                self.label.text = "في انتظار تحديثات من السيرفر..."
        except Exception:
            self.label.text = "فشل الاتصال بالسيرفر السحابي للاستقبال."

if __name__ == '__main__':
    TrackerApp().run()
