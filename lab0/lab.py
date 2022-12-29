# No Imports Allowed!


def backwards(sound):
    newsound = {'rate': sound['rate']}
    newsound['left'] = [x for x in reversed(sound['left'])]
    newsound['right'] = [x for x in reversed(sound['right'])]
    return newsound


def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:
        return None
    newsound = {'rate': sound1['rate']}
    newsound['left'] = [p*sound1['left'][i] + (1-p)*sound2['left'][i] for i in range(min(len(sound1['left']), len(sound2['left'])))]
    newsound['right'] = [p*sound1['right'][i] + (1-p)*sound2['right'][i] for i in range(min(len(sound1['right']), len(sound2['right'])))]
    return newsound

def echo(sound, num_echos, delay, scale):
    sample_delay = round(delay * sound['rate'])
    cur_l = sound['left']
    cur_r = sound['right']
    for i in range(1, num_echos+1):
        vals_l = [x * (scale ** i) for x in sound['left']]
        vals_r = [x * (scale ** i) for x in sound['right']]
        shif_vals_l = [0]*sample_delay*i + vals_l
        shif_vals_r = [0]*sample_delay*i + vals_r
        pad_cur_l = cur_l + [0]*(len(shif_vals_l)-len(cur_l))
        pad_cur_r = cur_r + [0]*(len(shif_vals_r)-len(cur_r))
        cur_l = [shif_vals_l[i] + pad_cur_l[i] for i in range(len(shif_vals_l))]
        cur_r = [shif_vals_r[i] + pad_cur_r[i] for i in range(len(shif_vals_r))]
    return {'rate': sound['rate'], 'left': cur_l, 'right': cur_r}


def pan(sound):
    newsound = {'rate': sound['rate']}
    num_samples = len(sound['left'])
    newsound['right'] = [sound['right'][i]*i/(num_samples-1) for i in range(num_samples)]
    newsound['left'] = [sound['left'][i]*(1-(i/(num_samples-1))) for i in range(num_samples)]
    return newsound


def remove_vocals(sound):
    new_vals = [sound['left'][i] - sound['right'][i] for i in range(len(sound['right']))]
    newsound = {'rate': sound['rate'], 'left': new_vals, 'right': new_vals}
    return newsound


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav('sounds/hello.wav')
    # mystery = load_wav('sounds/mystery.wav')
    # write_wav(backwards(mystery), 'backwardsmystery.wav')

    # synth = load_wav('sounds/synth.wav')
    # water = load_wav('sounds/water.wav')
    # write_wav(mix(synth, water, 0.2), 'synthwater.wav')

    # chord = load_wav('sounds/chord.wav')
    # write_wav(echo(chord, 5, 0.3, 0.6), 'chordecho.wav')

    # car = load_wav('sounds/car.wav')
    # write_wav(pan(car), 'pannedcar.wav')

    coffee = load_wav('sounds/coffee.wav')
    write_wav(remove_vocals(coffee), 'novocalcoffee.wav')

    # write_wav(backwards(hello), 'hello_reversed.wav')
