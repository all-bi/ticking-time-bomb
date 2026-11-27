import math
import os
import random
import struct
import wave

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SAMPLE_RATE = 44100


def ensure_assets_dir():
    os.makedirs(ASSETS_DIR, exist_ok=True)


def clamp(sample):
    return max(-0.98, min(0.98, sample))


def apply_fade(samples, fade_in_s, fade_out_s):
    fade_in_frames = max(1, int(fade_in_s * SAMPLE_RATE))
    fade_out_frames = max(1, int(fade_out_s * SAMPLE_RATE))
    total = len(samples)

    for index in range(total):
        sample = samples[index]
        if index < fade_in_frames:
            sample *= index / fade_in_frames
        if index >= total - fade_out_frames:
            sample *= max(0.0, (total - index - 1) / fade_out_frames)
        samples[index] = sample


def write_wav(path, samples):
    pcm_frames = bytearray()
    for sample in samples:
        value = int(clamp(sample) * 32767)
        pcm_frames.extend(struct.pack("<h", value))

    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(bytes(pcm_frames))


def tone(frequency, duration_s, amplitude=1.0, phase=0.0):
    frame_count = int(duration_s * SAMPLE_RATE)
    return [
        amplitude * math.sin((2.0 * math.pi * frequency * index / SAMPLE_RATE) + phase)
        for index in range(frame_count)
    ]


def white_noise(duration_s, amplitude=1.0):
    frame_count = int(duration_s * SAMPLE_RATE)
    return [amplitude * random.uniform(-1.0, 1.0) for _ in range(frame_count)]


def mix_layers(*layers):
    longest = max(len(layer) for layer in layers)
    mixed = [0.0] * longest
    for layer in layers:
        for index, sample in enumerate(layer):
            mixed[index] += sample
    return mixed


def normalize(samples, peak=0.96):
    max_value = max((abs(sample) for sample in samples), default=0.0)
    if max_value <= 0.0:
        return samples
    scale = peak / max_value
    return [sample * scale for sample in samples]


def soft_clip(samples, drive=1.0):
    clipped = []
    for sample in samples:
        clipped.append(math.tanh(sample * drive) / math.tanh(drive))
    return clipped


def low_pass(samples, smoothing=0.18):
    filtered = []
    previous = 0.0
    for sample in samples:
        previous += (sample - previous) * smoothing
        filtered.append(previous)
    return filtered


def envelope(samples, attack_s, decay_s):
    attacked = max(1, int(attack_s * SAMPLE_RATE))
    decayed = max(1, int(decay_s * SAMPLE_RATE))
    total = len(samples)
    shaped = []
    for index, sample in enumerate(samples):
        if index < attacked:
            gain = index / attacked
        else:
            distance = min(index - attacked, decayed)
            gain = math.exp(-3.6 * distance / decayed)
        if index > total - decayed:
            gain *= max(0.0, (total - index - 1) / decayed)
        shaped.append(sample * gain)
    return shaped


def generate_tick():
    beat_duration = 0.5
    hit = tone(1800, 0.016, amplitude=0.72)
    body = tone(940, 0.048, amplitude=0.36, phase=0.3)
    resonance = tone(280, 0.07, amplitude=0.18)
    noise = low_pass(white_noise(0.05, amplitude=0.09), smoothing=0.24)

    impact = mix_layers(
        hit + [0.0] * (int((beat_duration - 0.016) * SAMPLE_RATE)),
        body + [0.0] * (int((beat_duration - 0.048) * SAMPLE_RATE)),
        resonance + [0.0] * (int((beat_duration - 0.07) * SAMPLE_RATE)),
        noise + [0.0] * (int((beat_duration - 0.05) * SAMPLE_RATE)),
    )

    apply_fade(impact, 0.001, 0.07)
    return [sample * 0.68 for sample in impact]


def generate_explosion():
    duration_s = 1.95
    frame_count = int(duration_s * SAMPLE_RATE)

    sub_boom = envelope(tone(41, duration_s, amplitude=1.12), 0.001, 1.6)
    low_boom = envelope(tone(55, duration_s, amplitude=0.92, phase=0.2), 0.002, 1.42)
    mid_boom = envelope(tone(88, duration_s, amplitude=0.54, phase=0.7), 0.002, 1.12)
    punch = envelope(tone(128, duration_s, amplitude=0.26, phase=0.4), 0.001, 0.44)

    crack = envelope(tone(2100, 0.13, amplitude=0.42), 0.0006, 0.12)
    crack.extend([0.0] * (frame_count - len(crack)))

    slap = envelope(tone(940, 0.18, amplitude=0.34, phase=0.5), 0.0008, 0.14)
    slap.extend([0.0] * (frame_count - len(slap)))

    attack_noise = low_pass(white_noise(duration_s, amplitude=1.22), smoothing=0.038)
    attack_noise = envelope(attack_noise, 0.0008, 1.2)

    tail_noise = low_pass(white_noise(duration_s, amplitude=0.62), smoothing=0.014)
    tail_noise = envelope(tail_noise, 0.01, 1.9)

    wave_samples = mix_layers(
        sub_boom, low_boom, mid_boom, punch, crack, slap, attack_noise, tail_noise
    )
    apply_fade(wave_samples, 0.001, 0.18)
    wave_samples = soft_clip(wave_samples, drive=1.45)
    return normalize(wave_samples, peak=0.97)


def main():
    ensure_assets_dir()
    tick_path = os.path.join(ASSETS_DIR, "tick.wav")
    explosion_path = os.path.join(ASSETS_DIR, "explosion.wav")

    write_wav(tick_path, generate_tick())
    write_wav(explosion_path, generate_explosion())

    print("Vygenerováno:")
    for output_path in (tick_path, explosion_path):
        print(f"- {output_path} ({os.path.getsize(output_path)} B)")


if __name__ == "__main__":
    random.seed(7)
    main()
