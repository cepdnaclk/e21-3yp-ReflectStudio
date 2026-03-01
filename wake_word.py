import pvporcupine
import sounddevice as sd
import struct

def wait_for_wake_word():
    porcupine = pvporcupine.create(keywords=["Hey Mirror"])

    print("💤 Sleeping...")

    with sd.RawInputStream(
        samplerate=porcupine.sample_rate,
        blocksize=porcupine.frame_length,
        dtype='int16',
        channels=1
    ) as stream:

        while True:
            pcm, _ = stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("🔥 Wake word detected!")
                return
