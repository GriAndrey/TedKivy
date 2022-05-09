# dont forget install pyplayer (pip install pyplayer)
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from find import find_usage
import sqlite3
import random
import re


class TestApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.layout = MyLayout()
        return self.layout


class MyLayout(BoxLayout):
    video = ObjectProperty()
    text_input = ObjectProperty()
    sub = ObjectProperty()

    def __init__(self, **kwargs):

        self.video = None
        self.goodFinder = []
        super().__init__(**kwargs)

    # нахождение начала воспроизведения и длительности воспроизведения
    def on_loaded(self, *args):

        try:
            self.video.seek((self.goodFinder[0][4]/self.goodFinder[0][9])/1000 - 1/self.goodFinder[0][9], precise=True)
        except Exception as e:
            pass
        try:
            Clock.schedule_once(self.stop_playing, self.goodFinder[0][1]//1000+8)
        except IndexError as e:
            pass

    # нахождение в БД необохдиых видео и субтитров к нему по запросу
    def update_label(self, dt=0):
        self.video.state = "pause"
        self.video.source = ''
        req = self.text_input.text
        CONNECTION = sqlite3.connect('subtitles.db')
        finder = find_usage(req, CONNECTION)
        CONNECTION.close()
        self.goodFinder = []
        for i in finder:
            if re.search(rf'\b{req}\b', i[2].lower()) == None:
                continue
            self.goodFinder.append(i)
        if len(self.goodFinder) != 0:
            self.goodFinder = random.sample(self.goodFinder, 1)
            self.video.source = f'{self.goodFinder[0][5]}'
            self.video.state = "play"
            self.sub.text = f'{self.goodFinder[0][2]}'
            self.video.bind(loaded=self.on_loaded)
        else:

            self.sub.text = 'Not found anything'

    def start_playing(self):
        self.video.state = "pause"
        self.update_label()

    def stop_playing(self, t = 0):
        self.video.state = "pause"


TestApp().run()
