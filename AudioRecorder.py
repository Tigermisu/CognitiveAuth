from sys import byteorder
from array import array
from struct import pack
from time import time

import pyaudio
import wave

BASE_THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
TRIM_APPEND = RATE / 4

threshold = 500

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < threshold

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r


def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i) > threshold + BASE_THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)
    snd_data = _trim(snd_data)
    # I really don't know whats going on, but calling this twice works, and once does not.

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r

def record(timeConstrain):
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds of
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """
    global threshold
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    max_silent_samples = 30
    snd_started = False

    r = array('h')
    iterations = 0
    startTime = 0
    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)
        if iterations < 20:
            iterations += 1
            if(iterations == 20):
                #threshold = BASE_THRESHOLD + reduce(lambda x, y: abs(x) + abs(y), snd_data) / len(snd_data) #Avg noise
                threshold = BASE_THRESHOLD + max(snd_data)
                print("please speak a word into the microphone")
        elif silent and snd_started and timeConstrain == 0:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True
            if timeConstrain > 0:
                startTime = time()
        if snd_started and ((num_silent > max_silent_samples and timeConstrain == 0)
                            or (timeConstrain > 0 and time() - startTime > timeConstrain)):
            break
        elif snd_started and not silent:
            num_silent = 0

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = trim(r)
    r = normalize(r)
    r = add_silence(r, 0.5)
    return sample_width, r

def record_to_file(path, timeConstrain = 0):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record(timeConstrain)
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

if __name__ == '__main__':
    filename = 'audiosamples/%s.wav' % str(time()).split('.')[0]
    print("recording background noise")
    record_to_file(filename)
    print("done - result written to %s" % filename)