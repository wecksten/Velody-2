import mido
import time
import rtmidi
import random
import os
import filecmp
import glob
import ntpath

# simple midi player

def playFile(filename):
    port = mido.open_output()
    for msg in mido.MidiFile(filename):
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)

# count all velocities > 0

def getVelocityCount(filename):
    return getVelocityCountMinMax(filename, 1, 255)

# count all velocities in the range min, max

def getVelocityCountMinMax(filename, min, max):
    counter = 0
    mid = mido.MidiFile(filename)
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if (msg.type == 'note_on'):
                if (msg.velocity >= min and msg.velocity <= max):
                    counter += 1
    return counter

# calculate the average velocity

def getVelocityAverage(filename):
    velocity = 0
    counter = 0
    mid = mido.MidiFile(filename)
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if (msg.type == 'note_on'):
                if (msg.velocity > 0):
                    velocity += msg.velocity
                    counter += 1
    return (velocity / counter)

# calculate the velocity variance

def getVelocityVariance(filename):
    my = getVelocityAverage(filename)
    velocity = 0
    counter = 0
    mid = mido.MidiFile(filename)
    for i, track in enumerate(mid.tracks):
        for msg in track:
            if (msg.type == 'note_on'):
                if (msg.velocity > 0):
                    velocity += (msg.velocity - my) ** 2
                    counter += 1
    return (velocity / counter)

# generate n-bit modifier for encoding

def getNModifier(filename, bits):
    size = os.stat(filename).st_size
    for x in range(8):
        bit = size & 0x01
        modifier = bit * 2 ** (bits - 1) + random.randint(0, (2 ** (bits -1)-1))
        yield modifier
        size = size // 2
    with open(filename, "rb") as f:
        while (b := f.read(1)):
            c = ord(b)
            for x in range(8):
                bit = int(c) & 0x01
                modifier = bit * (2 ** (bits - 1)) + random.randint(0, (2 ** (bits -1)-1)  )
                yield modifier
                c = c // 2
    while (True):
        yield (random.randint(0,(2**bits)-1))

# encode n-bit file data or random data into velocity values

def encodeNLSB(inputDataFilename, inputMIDIFilename, outputMIDIFilename, bits, skew):
    count = 0    
    gen = getNModifier(inputDataFilename, bits)
    mid = mido.MidiFile(inputMIDIFilename)
    for i, track in enumerate(mid.tracks):   
        t = 0
        for msg in track:                        
            if (msg.type == 'note_on'):
                if (msg.velocity >= 2 ** bits):          
                    msg.velocity = (msg.velocity & (int(0xFF) - ((2 ** bits)-1))) | next(gen)
    mid.save(outputMIDIFilename)

# unpack extracted data

def convertNBits(data, bits):
    unmasked = data & ((2 ** bits) - 1)
    if (unmasked < 2 ** (bits-1)):
        return 0
    else:
        return 1

# extract n-bit data from velocity values

def decodeNLSB(inputMIDIFilename, outfile, bits):
    count = 0    
    line = []
    decodedData = []
    fileSize = 0
    decode = True
    mid = mido.MidiFile(inputMIDIFilename)
    for i, track in enumerate(mid.tracks):   
        t = 0
        for msg in track:                        
            if ((msg.type == 'note_on') & (decode == True)):
                if (msg.velocity >= 2 ** bits):
                    line.insert(0, convertNBits(msg.velocity,bits))
                    if (len(line) == 8):
                        if (fileSize == 0):
                            fileSize = decodeByte(line)
                            #print(fileSize)                            
                            line = []
                        else:
                            decodedData.append(decodeByte(line))
                            fileSize = fileSize - 1
                            line = []
                            if (fileSize == 0):                                                            
                                decode = False
    newFile = open(outfile, "wb")
    newFile.write(bytearray(decodedData))

def main():  
    # overall experiment settings

    # minimum number of bits to encode
    MIN_BITS = 4
    # maximum number of bits to encode
    MAX_BITS = 6
    midiFileList = glob.glob('./input-survey/*.mid')

    for bits in range(MIN_BITS,MAX_BITS+1):
        for midiFileInput in midiFileList:

            midiFileOutput = f'./output/Encoded_b{bits}_'+ntpath.basename(midiFileInput)

            inputFile = 'input.txt'
            outputFile = 'output.txt'

            max = getVelocityCountMinMax(midiFileInput, 2**bits, 128)
            count = encodeNLSB(inputFile, midiFileInput, midiFileOutput, bits, 0)
            decodeNLSB(midiFileOutput, outputFile, bits)
            avgIn = getVelocityAverage(midiFileInput)
            avgOut = getVelocityAverage(midiFileOutput)

            varIn = getVelocityVariance(midiFileInput)
            varOut = getVelocityVariance(midiFileOutput)

            totalEvents = getVelocityCountMinMax(midiFileInput, 1, 128)
            availableEvents = getVelocityCountMinMax(midiFileInput, 2**bits, 128)
            fileSize = os.stat(midiFileInput).st_size
            
            #
            #  filename & total events & events that can be used & amount of data that can be encoded & encoded bits per events total & bit encoding ration for whole file & difference in average velocity & difference in variance
            #  
            print (f'{midiFileInput} & {totalEvents} & {availableEvents} & {bits*availableEvents} & {bits*availableEvents/totalEvents} & {round(bits*availableEvents/(fileSize*8),4)} & {round(avgIn-avgOut,2)} & {round(varIn-varOut,2)} \\\\')

            if (filecmp.cmp(inputFile, outputFile) == False & os.stat(inputFile).st_size > 0):
                print (f'*** ERROR: Bad decode. Filename: {midiFileInput}')

if __name__ == "__main__":
    main()
