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
        self.schedule_repeating_event(self.auto_set_volume, None,15, 'AutoSetVolume')

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

    @intent_file_handler('reset.intent')
    def handle_volume_set_auto(self, message):
        wait_while_speaking()
        self.speak_dialog('messure.lowlevel')
        count = 0
        messure_thresh = 0
        timeout = time.time() + 20   # 5 minutes from now
        while True:
            if time.time() > timeout:
                break
            with io.open(self.filename, 'r') as fh:
                while True:
                    line = fh.readline()
                    if line == "":
                        break
                    # Ex:Energy:  cur=4 thresh=1.5
                    parts = line.split("=")
                    messure_thresh = messure_thresh + int(float(parts[-1]))
                    count = count + 1
                    self.log.info(line + " ==== " +str(count))
            time.sleep(1)
        messure_thresh = messure_thresh / count
        self.settings['LowNoice'] = messure_thresh + ((30 * messure_thresh) / 100)
        self.log.info("Setting LowNoice to: " + str(self.settings.get('LowNoice')))
        self.speak_dialog('messure.ok')  
        
        

    def auto_set_volume(self, message):
        if self.autovolume and not self.audio_service.is_playing:
            wait_while_speaking()
            with io.open(self.filename, 'r') as fh:
                while True:
                    line = fh.readline()
                    if line == "":
                        break

                    # Ex:Energy:  cur=4 thresh=1.5
                    parts = line.split("=")
                    meter_thresh = int(float(parts[-1]))
                    #meter_cur = float(parts[-2].split(" ")[0])
                    
                    lowlevel = self.settings.get('LowNoice') + int((30 * self.settings.get('LowNoice')) / 100)
                    
                    volume = 50
                    if meter_thresh < lowlevel:
                        volume = self.settings.get('Low volume')
                    else:
                        volume = self.settings.get('Normal volume')
                    self.log.info("Mesure mic: " + str(meter_thresh) + " Setting volume to :" + str(volume) + "%")
                    self.mixer.setvolume(volume)

                
            
def create_skill():
    return AutoSetVolume()

