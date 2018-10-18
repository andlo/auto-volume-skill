from mycroft import MycroftSkill, intent_file_handler
from mycroft.util import get_ipc_directory
from alsaaudio import Mixer
import io
import os
import os.path


   # Monitor IPC file containing microphone level info
   #   start_mic_monitor(os.path.join(get_ipc_directory(), "mic_level"))


  
class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
    
    def initialize(self):
        self.filename = os.path.join(get_ipc_directory(), "mic_level")
        self.mixer = Mixer()
        self.schedule_repeating_event(self.auto_set_volume, None,5, 'AutoSetVolume')
            

    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')

    def auto_set_volume(self, message):
        #global meter_cur
        global meter_thresh
        
        with io.open(self.filename, 'r') as fh:
            #fh.seek(0)
            while True:
                line = fh.readline()
                if line == "":
                    break

                # Just adjust meter settings
                # Ex:Energy:  cur=4 thresh=1.5
                parts = line.split("=")
                meter_thresh = int(float(parts[-1]))
                # meter_cur = float(parts[-2].split(" ")[0])
                
                # Store the thresh level
                if self.settings.get('HighNoice') == None:
                    self.settings['HighNoice'] = meter_thresh
                if self.settings.get('LowNoice') == None:
                    self.settings['LowNoice'] = meter_thresh
                
        
        
                if meter_thresh > self.settings.get('HighNoice'):
                    self.settings['HighNoice'] = meter_thresh
                elif meter_thresh < self.settings.get('LowNoice'):
                    self.settings['LowNoice'] = meter_thresh
                
                range = self.settings.get('HighNoice') - self.settings.get('LowNoice')
                lowlevel = int(self.settings.get('LowNoice') + (range/10))
                highlevel = int(self.settings.get('HighNoice') - (range/5)) 
                self.log.info("LovNoice: " + str(self.settings.get('LowNoice')) + 
                              " LowLevel: " + str(lowlevel) + 
                              " HighNoice :" + str(self.settings.get('HighNoice')) + 
                              " HighLevel: " + str(highlevel))

                volume = self.mixer.getvolume()
                if meter_thresh > highlevel:
                    volume = 75
                if meter_thresh < lowlevel:
                    volume = 35
                if meter_thresh < highlevel and meter_thresh > lowlevel:
                    volume = 60
                self.log.info("Mesure mic: " + str(meter_thresh) + " Setting volume to " + str(volume))
                self.mixer.setvolume(volume)

                
            
def create_skill():
    return AutoSetVolume()

