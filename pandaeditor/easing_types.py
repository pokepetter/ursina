'''Translated from https://github.com/AndrewRayCode/easing-utils/blob/master/src/easing.js'''

import math

def linear(t):
    return t

def ease_in_sine(t):
    return -1 * math.cos(t * (math.pi / 2)) + 1 #Slight acceleration from zero to full speed

def ease_out_sine(t):
    return math.sin(t * (math.pi / 2)) #Slight deceleration at the end

def ease_in_out_sine(t):
    return -.5 * (math.cos(math.pi * t) - 1) #Slight acceleration at beginning and slight deceleration at end

def ease_in_quad(t):
    return t * t #Accelerating from zero velocity

def ease_out_quad(t):
    return t * (2 - t) #Decelerating to zero velocity

def ease_in_out_quad(t):
    if t < .5:
        return 2 * t * t
    else:
        return - 1 + (4 - 2 * t) * t #Acceleration until halfway, then deceleration

def ease_in_cubic(t):
    return t * t * t #Accelerating from zero velocity

def ease_out_cubic(t): #Decelerating to zero velocity
    t1 = t - 1
    return t1 * t1 * t1 + 1

def ease_in_out_cubic(t): #Acceleration until halfway, then deceleration
    if t < .5:
        return 4 * t * t * t
    else:
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1

def ease_in_quart(t): #Accelerating from zero velocity
    return t * t * t * t

def ease_out_quart(t): #Decelerating to zero velocity
    t1 = t - 1
    return 1 - t1 * t1 * t1 * t1

def ease_in_out_quart(t): #Acceleration until halfway, then deceleration
    t1 = t - 1
    if t < .5:
        return 8 * t * t * t * t
    else:
        1 - 8 * t1 * t1 * t1 * t1

def ease_in_quint(t): #Accelerating from zero velocity
    return t * t * t * t * t

def ease_out_quint(t): #Decelerating to zero velocity
    t1 = t - 1
    return 1 + t1 * t1 * t1 * t1 * t1

def ease_in_out_quint(t): #Acceleration until halfway, then deceleration
    t1 = t - 1
    if t < .5:
        return 16 * t * t * t * t * t
    else:
        return 1 + 16 * t1 * t1 * t1 * t1 * t1

def ease_in_expo(t): #Accelerate _exponentially until finish
    return pow(2, 10 * (t - 1))

def ease_out_expo(t): #Initial _exponential acceleration slowing to stop
    return (-pow(2, -10 * t) + 1)

def ease_in_out_expo(t): #_exponential acceleration and deceleration
    scaledTime = t * 2
    scaledTime1 = scaledTime - 1

    if scaledTime < 1:
        return .5 * pow(2, 10 * (scaledTime1))

    return .5 * (-pow(2, -10 * scaledTime1) + 2)

def ease_in_circ(t): #Increasing velocity until stop
    scaledTime = t / 1
    return -1 * (math.sqrt(1 - scaledTime * t) - 1)

def ease_out_circ(t): #Start fast, decreasing velocity until stop
    t1 = t - 1
    return math.sqrt(1 - t1 * t1)

def ease_in_out_circ(t): #Fast increase in velocity, fast decrease in velocity
    scaledTime = t * 2
    scaledTime1 = scaledTime - 2

    if scaledTime < 1:
        return -.5 * (math.sqrt(1 - scaledTime * scaledTime) - 1)

    return .5 * (math.sqrt(1 - scaledTime1 * scaledTime1) + 1)

def ease_in_back(t, magnitude=1.70158): #Slow movement _backwards then fast snap to finish
    return t * t * ((magnitude + 1) * t - magnitude)

def ease_out_back(t, magnitude=1.70158): #Fast snap to _backwards point then slow resolve to finish
    scaledTime = (t / 1) - 1
    return (
        scaledTime * scaledTime * ((magnitude + 1) * scaledTime + magnitude)
    ) + 1

def ease_in_out_back(t, magnitude=1.70158): #Slow movement _backwards, fast snap to past finish, slow resolve to finish
    scaledTime = t * 2
    scaledTime2 = scaledTime - 2
    s = magnitude * 1.525

    if(scaledTime < 1):
        return .5 * scaledTime * scaledTime * (
            ((s + 1) * scaledTime) - s
        )
    return .5 * (
        scaledTime2 * scaledTime2 * ((s + 1) * scaledTime2 + s) + 2
    )

def ease_in_elastic(t, magnitude=.7): #_bounces slowly then quickly to finish
    if(t == 0 or t == 1):
        return t
    scaledTime = t / 1
    scaledTime1 = scaledTime - 1
    p = 1 - magnitude
    s = p / (2 * math.pi) * math.asin(1)

    return -(
        pow(2, 10 * scaledTime1) *
        math.sin((scaledTime1 - s) * (2 * math.pi) / p)
    )

def ease_out_elastic(t, magnitude=.7): #Fast acceleration, _bounces to zero
    p = 1 - magnitude
    scaledTime = t * 2

    if(t == 0 or t == 1):
        return t

    s = p / (2 * math.pi) * math.asin(1)
    return (
        pow(2, -10 * scaledTime) *
        math.sin((scaledTime - s) * (2 * math.pi) / p)
    ) + 1

def ease_in_out_elastic(t, magnitude=0.65): #Slow start and end, two _bounces sandwich a fast motion
    p = 1 - magnitude
    if(t == 0 or t == 1):
        return t

    scaledTime = t * 2
    scaledTime1 = scaledTime - 1
    s = p / (2 * math.pi) * math.asin(1)

    if(scaledTime < 1):
        return -.5 * (
            pow(2, 10 * scaledTime1) *
            math.sin((scaledTime1 - s) * (2 * math.pi) / p)
        )

    return (
        pow(2, -10 * scaledTime1) *
        math.sin((scaledTime1 - s) * (2 * math.pi) / p) * .5
    ) + 1

def ease_out_bounce(t): #_bounce to completion
    scaledTime = t / 1

    if scaledTime < (1 / 2.75):
        return 7.5625 * scaledTime * scaledTime

    elif scaledTime < (2 / 2.75):
        scaledTime2 = scaledTime - (1.5 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + .75

    elif scaledTime < (2.5 / 2.75):
        scaledTime2 = scaledTime - (2.25 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.9375

    else:
        scaledTime2 = scaledTime - (2.625 / 2.75)
        return (7.5625 * scaledTime2 * scaledTime2) + 0.984375

def ease_in_bounce(t): #_bounce increasing in velocity until completion
    return 1 - ease_out_bounce(1 - t)

def ease_in_out_bounce(t): #_bounce in and _bounce out
    if(t < .5):
        return ease_in_bounce(t * 2) * .5

    return (ease_out_bounce((t * 2) - 1) * .5) + .5



if __name__  == '__main__':
    from pandastuff import printvar
    import easing_types
    # test all the functions
    for i in dir(easing_types):
        item = getattr(easing_types, i)
        if callable(item):
            print(item.__name__, ':', item(.5))
