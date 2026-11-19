"""Apply the SNG comic narrator preset to a mono Russian speech stem."""
import argparse
import numpy as np
import parselmouth
from parselmouth.praat import call

def render(source, destination):
    speech = parselmouth.Sound(source)
    # Shift register and resonances separately, retaining original syllable timing.
    shaped = call(speech, "Change gender", 65, 370, 1.12, 185, 0.89, 1.0)
    values = shaped.values[0]
    values = np.pad(values, (0, max(0, speech.n_samples - len(values))))[:speech.n_samples]
    # Mild saturation shades stressed vowels while preserving quiet consonants.
    values = np.tanh(1.45 * values)
    original_rms = np.sqrt(np.mean(speech.values ** 2))
    values *= original_rms / max(1e-8, np.sqrt(np.mean(values ** 2)))
    values /= max(1, np.max(np.abs(values)) / 0.95)
    parselmouth.Sound(values, sampling_frequency=speech.sampling_frequency).save(destination, "WAV")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    render(args.source, args.destination)
