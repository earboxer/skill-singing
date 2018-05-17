# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


import random
from os.path import dirname, join
from subprocess import call

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.audioservice import AudioService
from mycroft.audio import wait_while_speaking
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play

class SingingSkill(MycroftSkill):
    def __init__(self):
        super(SingingSkill, self).__init__(name="SingingSkill")
        self.process = None
        self.play_list = {
            0: join(dirname(__file__), "popey-favourite.mp3"),
            1: join(dirname(__file__), "popey-jackson.mp3"),
            2: join(dirname(__file__), "popey-jerusalem.mp3"),
            3: join(dirname(__file__), "popey-lose-yourself.mp3"),
            4: join(dirname(__file__), "popey-lovemetender.mp3"),
            5: join(dirname(__file__), "popey-rocketman.mp3"),
            6: join(dirname(__file__), "amazinggrace"),
        }

    def initialize(self):
        self.audioservice = AudioService(self.emitter)
        self.add_event("mycroft.sing", self.sing, False)

    def sing(self, message):
        self.process = play_mp3(self.play_list[3])

    @intent_handler(IntentBuilder('').require('Sing'))
    def handle_sing(self, message):
        path = random.choice(self.play_list)
        path = self.play_list[6]
        try:
            self.speak_dialog('singing')
            track = self.create_song(path)
            wait_while_speaking()
            play(track)
            #self.audioservice.play(path)
        except Exception as e:
            self.log.error("Error: {0}".format(e))

    def create_song(path):
        # Create and load audio
        # TODO: use tmp file instead of main.wav
        tmp_voice_file = "/tmp/main.wav"
        call(['mimic', path + ".ssml", '-o', tmp_voice_file, '-ssml'])
        voice = AudioSegment.from_wav(tmp_voice_file)
        track = AudioSegment.from_wav(path + ".wav")
        # Read the file of spaces
        with open(path+".time.txt") as f:
            timing = f.readlines()
        timing = [int(x.strip()) for x in timing]
        # Splice the audio together with the spaces.
        i = 0
        split_segments = split_on_silence(voice, 100, -64)
        if len(split_segments) != len(timing):
            self.log.error("Error: mismatched audio and spacing.")
        for chunk in split_segments:
            track = track.overlay(chunk, position=timing[i])
            i = i+1
        # Return the AudioSegment so it can be played after we've waited.
        return track

    def stop(self):
        if self.process and self.process.poll() is None:
            self.speak_dialog('singing.stop')
            self.process.terminate()
            self.process.wait()


def create_skill():
    return SingingSkill()
