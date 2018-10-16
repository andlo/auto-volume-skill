from mycroft import MycroftSkill, intent_file_handler

from mycroft.util import get_ipc_directory
import os
import os.path

   # Monitor IPC file containing microphone level info
   #   start_mic_monitor(os.path.join(get_ipc_directory(), "mic_level"))


  def read_file_from(self, bytefrom):
        global meter_cur
        global meter_thresh

        with io.open(self.filename, 'r') as fh:
            fh.seek(bytefrom)
            while True:
                line = fh.readline()
                if line == "":
                    break

                # Just adjust meter settings
                # Ex:Energy:  cur=4 thresh=1.5
                parts = line.split("=")
                meter_thresh = float(parts[-1])
                meter_cur = float(parts[-2].split(" ")[0])




class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.filename=os.path.join(get_ipc_directory(), "mic_level")
        self.level = 25
        auto_set_volume(self)

    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')

    def auto_set_volume(self):
        global meter_cur
        global meter_thresh

        with io.open(self.filename, 'r') as fh:
            fh.seek(bytefrom)
            while True:
                line = fh.readline()
                if line == "":
                    break

                # Just adjust meter settings
                # Ex:Energy:  cur=4 thresh=1.5
                parts = line.split("=")
                meter_thresh = float(parts[-1])
                meter_cur = float(parts[-2].split(" ")[0])
                self.level = int(meter_cur)*10
                set_volume(self)

    def set_volume(self):
        #level = self.__get_volume_level(message, self.mixer.getvolume()[0])
        self.mixer.setvolume(self.level)
        


def create_skill():
    return AutoSetVolume()

