"""
skill auto-volume
Copyright (C) 2018  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util import get_ipc_directory
from mycroft.audio import wait_while_speaking
from mycroft.skills.audioservice import AudioService
from alsaaudio import Mixer
import io
import os
import os.path
import time


class AutoVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.filename = os.path.join(get_ipc_directory(), "mic_level")
        self.audio_service = AudioService(self.bus)
        self.mixer = Mixer()
        self.schedule_repeating_event(self.auto_set_volume, None, 5, 'AutoVolume')
        self.schedule_repeating_event(self.mesure_mic_thresh, None, 1, 'AutoVolume_messure')

        self.autovolume = True
        if self.settings.get('High volume') is None:
            self.settings['High volume'] = 75
        if self.settings.get('Normal volume') is None:
            self.settings['Normal volume'] = 60
        if self.settings.get('Low volume') is None:
            self.settings['Low volume'] = 35

        wait_while_speaking()
        with io.open(self.filename, 'r') as fh:
            while True:
                line = fh.readline()
                if line == "":
                    break
                # Energy:  cur=4 thresh=4.773 muted=0
                meter_thresh = float(line.split("=")[2].split(" ")[0])

        if self.settings.get('Highest messurement') is None:
            self.settings['Highest messurement'] = meter_thresh
        if self.settings.get('Lowest messurement') is None:
            self.settings['Lowest messurement'] = meter_thresh

        self.volume = int(self.settings.get('Low volume'))
        self.meter_thresh = 0
        self.meter_high = meter_thresh
        self.meter_low = meter_thresh
        self.meter_thresh_list = []
        self.meter_thresh_list.append(meter_thresh)

        self.add_event('recognizer_loop:record_begin',
                       self.handle_listener_started)
        self.add_event('recognizer_loop:record_end',
                       self.handle_listener_ended)



    def handle_listener_started(self, message):
        self.autovolume = False

    def handle_listener_ended(self, message):
        time.sleep(5)
        self.autovolume = True

    @intent_file_handler('activate.intent')
    def handle_activate(self, message):
        self.autovolume = True
        self.speak_dialog("activate")

    @intent_file_handler('deactivate.intent')
    def handle_deactivate(self, message):
        self.autovolume = False
        self.speak_dialog("deactivate")

    @intent_file_handler('reset.intent')
    def handle_reset(self, message):
        self.speak_dialog("reset")
        wait_while_speaking()
        with io.open(self.filename, 'r') as fh:
            while True:
                line = fh.readline()
                if line == "":
                    break
                # Energy:  cur=4 thresh=4.773 muted=0
                meter_thresh = float(line.split("=")[2].split(" ")[0])

        self.settings['Highest messurement'] = meter_thresh
        self.settings['Lowest messurement'] = meter_thresh

        self.volume = int(self.settings.get('Low volume'))
        self.meter_thresh = 0
        self.meter_high = meter_thresh
        self.meter_low = meter_thresh
        self.meter_thresh_list = []
        self.meter_thresh_list.append(meter_thresh)

    def mesure_mic_thresh(self, message):
        if self.autovolume and not self.audio_service.is_playing:
            wait_while_speaking()
            with io.open(self.filename, 'r') as fh:
                while True:
                    line = fh.readline()
                    if line == "":
                        break
                    # Energy:  cur=4 thresh=4.773 muted=0
                    meter_thresh = float(line.split("=")[2].split(" ")[0])

                    self.meter_thresh_list.append(meter_thresh)
                    if len(self.meter_thresh_list) > 120:
                        self.meter_thresh_list.pop(1)

                    self.meter_thresh = sum(self.meter_thresh_list) / float(len(self.meter_thresh_list))

                    if self.meter_thresh < self.settings.get('Lowest messurement'):
                        self.settings['Lowest messurement'] = self.meter_thresh
                    if self.meter_thresh > self.settings.get('Highest messurement'):
                        self.settings['Highest messurement'] = self.meter_thresh

    def auto_set_volume(self, message):
        if self.autovolume and not self.audio_service.is_playing:
            wait_while_speaking()

            volume = int(self.settings.get('Normal volume'))
            range = self.settings.get('Highest messurement') - self.settings.get('Lowest messurement')
            high_level = self.settings.get('Highest messurement') - ((10 * range) / 100)
            low_level = self.settings.get('Lowest messurement') + ((10 * range) / 100)

            if self.meter_thresh > high_level:
                volume = self.settings.get('High volume')
            if self.meter_thresh < low_level:
                volume = self.settings.get('Low volume')

            if volume != self.volume and volume is not None:
                self.mixer.setvolume(int(volume))
                self.volume = volume
                self.log.info("Mic thresh: " + str(self.meter_thresh) +
                              " Low level: " + str(low_level) +
                              " High level: " + str(high_level))
                self.log.info("Setting volume to :" + str(volume) + "%")


def create_skill():
    return AutoVolume()
