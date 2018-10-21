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
        if self.settings.get('Messurement list') == None:
            self.settings['Messurement list'] = []
        
        self.meter_thresh = 0
        self.meter_high = meter_thresh
        self.meter_low = meter_thresh
        self.meter_thresh_list = []

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
                    
                    #self.log.info("Mesure mic: " + str(meter_thresh))
                    #self.log.info("Meter low: " + str(self.meter_low) + " level: " + str( self.meter_low + ((30 * self.meter_low) / 100)))
                    #self.log.info("Meter high: " + str(self.meter_high) + " level: " + str(self.meter_high - ((10 * self.meter_high) / 100)))
                    #self.log.info("meter_thresh_list: " + str(len(self.meter_thresh_list)))  

                    self.settings['Messurement list'].append(meter_thresh)
                    if len(self.meter_thresh_list) > 120:
                        self.meter_thresh_list.pop(1)
                    self.meter_thresh = sum(self.meter_thresh_list) / float(len(self.meter_thresh_list))  
                                        
                    if self.meter_thresh < self.meter_low:
                        self.meter_low = self.meter_thresh
                    if self.meter_thresh > self.meter_high:
                        self.meter_high = self.meter_thresh
                    


    def auto_set_volume(self, message):
        if len(self.meter_thresh_list) == 120:
            if self.autovolume and not self.audio_service.is_playing:
                wait_while_speaking()
                volume = self.settings.get('Normal volume')
                if self.meter_thresh > self.meter_high - ((10 * self.meter_high) / 100):
                    volume = self.settings.get('High volume')
                if self.meter_thresh < self.meter_low + ((30 * self.meter_low) / 100):
                    volume = self.settings.get('Low volume')
                self.log.info("Mesure mic: " + str(self.meter_thresh) + 
                              " Setting volume to :" + str(volume) + "%" + 
                              " from " + str(self.mixer.getvolume()) + "%")
                if not volume == None:  
                    self.mixer.setvolume(volume)
        else:
            self.log.info("Running initial messurement. ") 
            self.log.info("Meter low: " + str(self.meter_low) + " level: " + str( self.meter_low + ((30 * self.meter_low) / 100)))
            self.log.info("Meter high: " + str(self.meter_high) + " level: " + str(self.meter_high - ((10 * self.meter_high) / 100)))
            self.log.info("meter_thresh_list: " + str(len(self.meter_thresh_list)))  


 
            
def create_skill():
    return AutoSetVolume()

