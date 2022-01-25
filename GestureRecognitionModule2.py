import math
from enum import Enum


class GestureRecognitionModule:

    class State(Enum):
        NORMAL = 0
        VOLUME = 1
        FF_REWIND = 2
        PREV_NEXT = 3
        WAITING = 4

    class Gesture(Enum):
        PLAY = 0
        PAUSE = 1

    def __init__(self):
        self.suc_frames = 0                     #gi brojam frejmovite vo koj imam consistent znak
        self.prev_position = ''                 #prethodnata pozicija mi sluzi za da brojam frames
        self.state = self.State.NORMAL          #sosotojbata vo koja se naogja klasata
        self.swipe_frame = 0                    #mi pomaga za da presmetam dali ima swipe
        self.prev_pointer_position = 0          #mi pomaga za da presmetam dali ima swipe
        self.volume_pointer = None              #position for volume control
        self.no_hand = 0                        #frames without hand

    def get_swipe(self, pointer):
        if self.swipe_frame == 0:
            self.prev_pointer_position = pointer

        self.swipe_frame += 1

        if self.swipe_frame % 5 == 0:
            dist = pointer - self.prev_pointer_position

            if dist > 30:
                self.swipe_frame = 0
                return 'LEFT'
            if dist < -30:
                self.swipe_frame = 0
                return 'RIGHT'

            self.prev_pointer_position = pointer

        return ''

    def volume_control(self, pointer):
        change = abs(int((self.volume_pointer - pointer) / 30))
        if change > 9:
            change = 9
        return f'VOLUME {change}'

    def ff_rewind_control(self, pointer):
        while True:
            swipe = self.get_swipe(pointer)
            if not swipe.__eq__(''):
                break

            return 'Swipe'

        self.state = self.State.WAITING

        if swipe == 'RIGHT':
            return 'REWIND'
        else:
            return 'FF'

    def switch_video_control(self, pointer):
        while True:
            swipe = self.get_swipe(pointer)
            if not swipe.__eq__(''):
                break

            return 'Swipe'

        self.state = self.State.WAITING

        if swipe == 'RIGHT':
            return 'PREV'
        else:
            return 'NEXT'

    def check_gesture(self, position, pointer):

        if position.__eq__(''):
            self.no_hand += 1
        else:
            self.no_hand = 0

        if self.no_hand >= 5:
            self.state = self.State.NORMAL
            return ''

        if position.__eq__('011111'):
            self.state = self.State.NORMAL
            return self.recognise_gesture(position)

        if self.state == self.State.WAITING:
            return 'Do a fist'

        if self.state == self.State.NORMAL:
            self.volume_pointer = None
            return self.recognise_gesture(position)

        if self.state == self.State.VOLUME:
            if self.volume_pointer is None:
                self.volume_pointer = pointer

            return self.volume_control(pointer)

        if self.state == self.State.FF_REWIND:
            return self.ff_rewind_control(pointer)

        if self.state == self.State.PREV_NEXT:
            return self.switch_video_control(pointer)

    def recognise_gesture(self, position):

        if position == '000000':
            return 'PAUSE'

        elif position == '101111':
            return 'PLAY'

        elif position == '010111':
            self.state = self.State.FF_REWIND
            return 'FF/REWIND'

        elif position == '010011':
            self.state = self.State.VOLUME
            return 'VOLUME CONTROL'

        elif position == '010000':
            self.state = self.State.PREV_NEXT
            return 'CHANGE VIDEO'

        else:
            return 'NOT RECOGNIZED'

    def get_gesture(self, position: str, pointer):

        if self.state != self.State.NORMAL:
            return self.check_gesture(position, pointer)

        if position.__eq__(self.prev_position):
            self.suc_frames += 1

        elif not position.__eq__(self.prev_position):
            self.suc_frames = 0
            self.prev_position = position
            return ''

        if self.suc_frames == 5:
            self.suc_frames = 0
            return self.check_gesture(position, pointer)

        else:
            return ''



#agol palec pokazalec sreden prsten mal


# NORMAL VOLUME FF/REWIND NEXT/PREV

# PAUSE ; PLAY ; FF/REWIND -> SWIPE -> FF, Rewind ; VOLUME CONTROL -> VOLUME {num} ; CHANGE VIDEO -> SWIPE -> NEXT , PREV