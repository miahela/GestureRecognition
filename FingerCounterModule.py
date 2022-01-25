import math


def get_angle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang


def dist(x, y):
    return math.sqrt(math.pow(x[0] - y[0], 2) + math.pow(x[1] - y[1], 2))


def get_fingers(landmarks):

    fingers = ''

    if len(landmarks) != 0:
        if landmarks[17][1] > landmarks[1][1]:
            fingers += '1'
        else:
            fingers += '0'

        if dist(landmarks[4], landmarks[9]) < 30 or \
                dist(landmarks[4], landmarks[13]) < 30:
            fingers += '1'
        else:
            fingers += '0'

        # for i in range(5, 18, 4):
        #    p1, p2 = landmarks[i], landmarks[i + 3]
        #    t1, t2, t3 = landmarks[i], landmarks[i+1], landmarks[i+2]
        #    if dist(p1, p2) < 26:
        #        fingers += '1'
        #    else:
        #        fingers += '0'
        #    if i == 5:
        #        print(i, t1, t2, t3, get_angle(t1, t2, t3))

        for i in range(5, 18, 4):
            t1, t2, t3 = landmarks[i], landmarks[i + 1], landmarks[i + 2]
            ang = get_angle(t1, t2, t3)
            if ang < 130 or ang > 240:
                fingers += '1'
            else:
                fingers += '0'

    return fingers
