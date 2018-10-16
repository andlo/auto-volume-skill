from mycroft import MycroftSkill, intent_file_handler


class AutoSetVolume(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('volume.set.auto.intent')
    def handle_volume_set_auto(self, message):
        self.speak_dialog('volume.set.auto')


def create_skill():
    return AutoSetVolume()

