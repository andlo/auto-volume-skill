from mycroft import MycroftSkill, intent_file_handler
from mycroft.util import get_ipc_directory
#from mycroft.util import wait_while_speaking
from mycroft.audio import wait_while_speaking
from mycroft.skills.audioservice import AudioService
from alsaaudio import Mixer
import io
import os
import os.path
import time

 
class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
    
    def initialize(self):
        self.filename = os.path.join(get_ipc_directory(), "mic_level")
        self.audio_service = AudioService(self.bus)
        self.mixer = Mixer()
        self.schedule_repeating_event(self.auto_set_volume, None,5, 'AutoSetVolume')
        self.schedule_repeating_event(self.mesure_mic_thresh, None,1, 'AutoSetVolume_messure')

        self.autovolume = True
        if self.settings.get('High volume') == None:
            self.settings['High volume'] = 75
        if self.settings.get('Normal volume') == None:
            self.settings['Normal volume'] = 60
        if self.settings.get('Low volume') == None:
            self.settings['Low volume'] = 35

        self.add_event('recognizer_loop:record_begin',  
                    self.handle_listener_started)  
        self.add_event('recognizer_loop:record_end',  
                    self.handle_listener_ended)

        wait_while_speaking()
        with io.open(self.filename, 'r') as fh:
            while True:
                line = fh.readline()
                if line == "":
                    break
                # Ex:Energy:  cur=4 thresh=1.5
                parts = line.split("=")
                meter_thresh = float(parts[-1])
        
        if self.settings.get('Highest messurement') == None:
            self.settings['Highest messurement'] = meter_thresh
        if self.settings.get('Lowest messurement') == None:
            self.settings['Lowest messurement'] = meter_thresh
        
        self.volume = self.settings.get('Low volume')
        self.meter_thresh = 0
        self.meter_high = meter_thresh
        self.meter_low = meter_thresh
        self.meter_thresh_list = [meter_thresh]

    def handle_listener_started(self, message):  
        # code to excecute when active listening begins...
        self.autovolume = False

    def handle_listener_ended(self, message):  
        # code to excecute when active listening begins...  
        time.sleep(5)
        self.autovolume = True
                   

    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')

    def mesure_mic_thresh(self, message):
        if self.autovolume and not self.audio_service.is_playing:
            wait_while_speaking()
            with io.open(self.filename, 'r') as fh:
                while True:
                    line = fh.readline()
                    if line == "":
                        break
                    # Ex:Energy:  cur=4 thresh=1.5
                    parts = line.split("=")
                    meter_thresh = float(parts[-1])
                    #meter_cur = float(parts[-2].split(" ")[0])
   
                    self.meter_thresh_list.append(meter_thresh)
                    if len(self.meter_thresh_list) > 120:
                        self.meter_thresh_list.pop(1)
                    
                    self.meter_thresh = sum(self.meter_thresh_list) / float(len(self.meter_thresh_list))  
                                        
                    if self.meter_thresh < self.settings.get('Lowest messurement'):
                        self.settings['Lowest messurement'] = self.meter_thresh
                    if self.meter_thresh > self.settings.get('Highest messurement'):
                        self.settings['Highest messurement'] = self.meter_thresh

    def auto_set_volume(self, message):
        #if len(self.meter_thresh_list) > 60:
        if self.autovolume and not self.audio_service.is_playing:
            wait_while_speaking()

            volume = self.settings.get('Normal volume')
            range = self.settings.get('Highest messurement') - self.settings.get('Lowest messurement')
            high_level = self.settings.get('Highest messurement') - ((10 * range) / 100)
            low_level = self.settings.get('Lowest messurement') + ((10 * range) / 100)

            if self.meter_thresh > high_level:
                volume = self.settings.get('High volume')
            if self.meter_thresh < lov_level:
                volume = self.settings.get('Low volume')

            if volume != self.volume and volume != None:  
                self.mixer.setvolume(volume)
                self.volume = volume
                self.log.info("Mic thresh: " + str(self.meter_thresh) + 
                            " Low level: " + str(low_level) +
                            " High level: " + str(high_level))
                self.log.info("Setting volume to :" + str(volume)  + "%")
    

 
            
def create_skill():
    return AutoSetVolume()

