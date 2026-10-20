"""
NeoPixel 16-LED RGBW Ring Test & Effects for MicroPython

Compatible with:
- Adafruit NeoPixel Ring - 16 x 5050 RGBW LEDs (SKU 2856, etc.)
- MicroPython boards (Raspberry Pi Pico / RP2040, ESP32, ESP8266, etc.)
"""

import time
import random
from machine import Pin
import neopixel

# ==============================================================================
# Configuration
# ==============================================================================
# Change PIN_NUM to match the GPIO pin connected to the NeoPixel Data In (DI) pin:
#   - Raspberry Pi Pico / RP2040: Pin(0), Pin(15), Pin(16), Pin(28), etc.
#   - ESP32: Pin(4), Pin(5), Pin(13), Pin(14), etc.
#   - ESP8266: Pin(4) (D2), Pin(5) (D1), etc.
PIN_NUM = 0

NUM_PIXELS = 16

# RGBW rings require 4 bytes per pixel (Red, Green, Blue, White)
# Default in MicroPython is 3 (RGB). Set bpp=4 for RGBW.
BPP = 4

# Brightness factor (0.0 to 1.0)
# RGBW rings at 1.0 can draw ~0.9A and are extremely bright!
# 0.1 to 0.3 is recommended for tabletop testing.
GLOBAL_BRIGHTNESS = 0.25

# Initialize NeoPixel strip
pixel_pin = Pin(PIN_NUM, Pin.OUT)
np = neopixel.NeoPixel(pixel_pin, NUM_PIXELS, bpp=BPP)


# ==============================================================================
# Helper Utilities
# ==============================================================================
def apply_brightness(color, brightness=GLOBAL_BRIGHTNESS):
    """Scale an (R, G, B, W) or (R, G, B) tuple by the brightness factor."""
    return tuple(int(c * brightness) for c in color)


def set_pixel(index, color, brightness=GLOBAL_BRIGHTNESS):
    """Set a pixel with automatic brightness scaling and 4-tuple normalization."""
    # Ensure color tuple has 4 elements (R, G, B, W)
    if len(color) == 3:
        color = (color[0], color[1], color[2], 0)
    scaled = apply_brightness(color, brightness)
    np[index % NUM_PIXELS] = scaled


def fill(color, brightness=GLOBAL_BRIGHTNESS):
    """Fill the entire ring with a color and update."""
    if len(color) == 3:
        color = (color[0], color[1], color[2], 0)
    scaled = apply_brightness(color, brightness)
    np.fill(scaled)
    np.write()


def clear():
    """Turn off all LEDs."""
    np.fill((0, 0, 0, 0))
    np.write()


def color_wheel(pos):
    """Generate rainbow colors across 0-255 positions (R, G, B, W=0)."""
    pos = pos & 255
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3, 0)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3, 0)


# ==============================================================================
# Example Effects
# ==============================================================================

def test_channels():
    """Diagnostic check: cycle through Red, Green, Blue, and White channels."""
    print("Channel Check: Red -> Green -> Blue -> White")
    channels = [
        ("Red",   (255,   0,   0,   0)),
        ("Green", (  0, 255,   0,   0)),
        ("Blue",  (  0,   0, 255,   0)),
        ("White", (  0,   0,   0, 255)),
    ]
    for name, col in channels:
        print(f"  Showing {name} channel...")
        fill(col)
        time.sleep(0.8)
    clear()
    time.sleep(0.3)


def color_wipe(color, wait_ms=40):
    """Wipe a color across the ring one pixel at a time."""
    for i in range(NUM_PIXELS):
        set_pixel(i, color)
        np.write()
        time.sleep_ms(wait_ms)


def theater_chase(color, wait_ms=80, cycles=6):
    """Theater-style crawling marquee lights."""
    for _ in range(cycles):
        for q in range(3):
            for i in range(0, NUM_PIXELS, 3):
                if i + q < NUM_PIXELS:
                    set_pixel(i + q, color)
            np.write()
            time.sleep_ms(wait_ms)
            for i in range(0, NUM_PIXELS, 3):
                if i + q < NUM_PIXELS:
                    np[i + q] = (0, 0, 0, 0)


def rainbow_cycle(wait_ms=5, loops=2, step=2):
    """Fast, smooth rainbow distributed evenly across all 16 ring LEDs."""
    for j in range(0, 256 * loops, step):
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            col = color_wheel(pixel_index & 255)
            set_pixel(i, col)
        np.write()
        if wait_ms > 0:
            time.sleep_ms(wait_ms)


def comet(color, tail_length=5, wait_ms=35, rotations=4):
    """A comet/spinner head with a fading tail spinning around the ring."""
    total_steps = NUM_PIXELS * rotations
    for step in range(total_steps):
        clear()
        for t in range(tail_length):
            idx = (step - t) % NUM_PIXELS
            fade_factor = (tail_length - t) / tail_length
            faded_color = tuple(int(c * fade_factor) for c in color)
            set_pixel(idx, faded_color)
        np.write()
        time.sleep_ms(wait_ms)


def white_pulse(wait_ms=20, pulses=2):
    """Smooth breathing effect using the dedicated Warm/Cool White LED channel."""
    for _ in range(pulses):
        # Fade up
        for b in range(0, 101, 2):
            level = int((b / 100.0) * 255 * GLOBAL_BRIGHTNESS)
            np.fill((0, 0, 0, level))
            np.write()
            time.sleep_ms(wait_ms)
        # Fade down
        for b in range(100, -1, -2):
            level = int((b / 100.0) * 255 * GLOBAL_BRIGHTNESS)
            np.fill((0, 0, 0, level))
            np.write()
            time.sleep_ms(wait_ms)


def sparkle(color, sparkles=40, wait_ms=40):
    """Random LEDs twinkle on and off."""
    clear()
    for _ in range(sparkles):
        idx = random.randint(0, NUM_PIXELS - 1)
        set_pixel(idx, color)
        np.write()
        time.sleep_ms(wait_ms)
        np[idx] = (0, 0, 0, 0)
        np.write()
        time.sleep_ms(wait_ms // 2)


def dual_chasers(wait_ms=45, rotations=8):
    """Two heads running in opposite directions with distinct colors."""
    total_steps = NUM_PIXELS * rotations
    for step in range(total_steps):
        clear()
        p1 = step % NUM_PIXELS
        p2 = (NUM_PIXELS - 1 - (step % NUM_PIXELS)) % NUM_PIXELS
        
        # Chaser 1: Cyan / Light Blue (RGB)
        set_pixel(p1, (0, 180, 255, 0))
        # Chaser 2: Pure White channel
        set_pixel(p2, (0, 0, 0, 255))
        
        # When they collide, blend both
        if p1 == p2:
            set_pixel(p1, (0, 180, 255, 255))
            
        np.write()
        time.sleep_ms(wait_ms)


def fire(duration_s=8, wait_ms=35, warmup_s=2.5):
    """
    Campfire / flame effect that kindles slowly from embers and builds into a roaring fire.
    Uses heat diffusion around the ring plus red, orange, and warm white channels.
    """
    heat = [0] * NUM_PIXELS
    # Seed a couple of initial low embers to catch the flame
    seed = random.randint(0, NUM_PIXELS - 1)
    heat[seed] = 45
    heat[(seed + 1) % NUM_PIXELS] = 25

    start_time = time.ticks_ms()
    total_ms = int(duration_s * 1000)
    warmup_ms = int(warmup_s * 1000)

    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time)
        if elapsed >= total_ms:
            break

        # Slow exponential curve for organic kindling buildup
        if elapsed < warmup_ms:
            warmup_factor = (elapsed / warmup_ms) ** 1.6
        else:
            warmup_factor = 1.0

        for i in range(NUM_PIXELS):
            # Heat diffusion: blend with neighboring pixels to simulate fire catching & spreading
            prev_i = (i - 1) % NUM_PIXELS
            next_i = (i + 1) % NUM_PIXELS
            diffused = (heat[prev_i] + heat[i] * 2 + heat[next_i]) // 4

            # Natural thermal fluctuation scaled by the warmup factor
            flicker = random.randint(-25, int(35 * warmup_factor) + 5)
            new_heat = diffused + flicker

            max_ceiling = int(255 * warmup_factor)
            min_floor = int(35 * warmup_factor)

            # Random flare-ups intensify as the fire grows
            if warmup_factor > 0.35 and random.randint(0, 100) < int(8 * warmup_factor):
                new_heat = random.randint(int(170 * warmup_factor), max_ceiling)

            heat[i] = max(min_floor, min(max_ceiling, new_heat))

            h = heat[i]
            if h <= 4:
                set_pixel(i, (0, 0, 0, 0))
                continue

            # Map heat to (Red, Green, Blue, White)
            r = min(255, int(h * 1.15))
            g = max(0, min(255, int(h * 0.42) - 12))
            b = 0
            # Inject white channel at high heat to simulate glowing ember cores
            w = int((h - 150) * 0.75) if h > 150 else 0

            set_pixel(i, (r, g, b, w))

        np.write()
        time.sleep_ms(wait_ms)

    # Gentle cool-down into darkness
    for _ in range(16):
        for i in range(NUM_PIXELS):
            heat[i] = max(0, heat[i] - 16)
            h = heat[i]
            r = min(255, int(h * 1.15))
            g = max(0, min(255, int(h * 0.42) - 12))
            b = 0
            w = int((h - 150) * 0.75) if h > 150 else 0
            set_pixel(i, (r, g, b, w))
        np.write()
        time.sleep_ms(wait_ms)

    clear()


def explosion(count=1):
    """
    Simulates an explosion sequence:
    1. Fuse / Ignition: Accelerating spark racing around the ring.
    2. Detonation: Intense white-hot flash across the whole ring.
    3. Fireball: Expanding fiery blast.
    4. Cooling Embers: Scattered sparks fading from white-hot -> orange -> red -> dark.
    """
    for boom in range(count):
        # 1. Accelerating Fuse Spark (1 revolution, speeding up)
        delay = 45
        for i in range(NUM_PIXELS):
            clear()
            # Spark head with red trailing ember
            set_pixel(i, (255, 180, 0, 100))
            if i > 0:
                set_pixel(i - 1, (120, 20, 0, 0))
            np.write()
            time.sleep_ms(delay)
            delay = max(8, delay - 3)

        # Micro-pause of anticipation right before detonation
        clear()
        time.sleep_ms(40)

        # 2. Instant Blinding Detonation Flash (Full White + Amber fireball)
        fill((255, 230, 140, 255), brightness=min(1.0, GLOBAL_BRIGHTNESS * 1.5))
        time.sleep_ms(60)

        # 3. Fireball expansion / decay
        fill((255, 90, 0, 50))
        time.sleep_ms(70)

        # 4. Scattered Cooling Embers Fallout
        embers = [random.randint(60, 255) if random.random() < 0.75 else 0 for _ in range(NUM_PIXELS)]

        for _ in range(35):
            all_dead = True
            for i in range(NUM_PIXELS):
                if embers[i] > 0:
                    all_dead = False
                    # Cool down by a random amount
                    embers[i] = max(0, embers[i] - random.randint(8, 18))
                    h = embers[i]

                    # Color shift as ember cools: white-hot -> orange -> dark red -> out
                    r = min(255, int(h * 1.2))
                    g = max(0, int((h - 50) * 0.4))
                    b = 0
                    w = int((h - 170) * 0.8) if h > 170 else 0
                    set_pixel(i, (r, g, b, w))
                else:
                    np[i] = (0, 0, 0, 0)

            # Occasional crackle / flare on surviving embers
            if random.random() < 0.2:
                hot_idx = random.randint(0, NUM_PIXELS - 1)
                if embers[hot_idx] > 30:
                    embers[hot_idx] = min(255, embers[hot_idx] + random.randint(20, 50))

            np.write()
            time.sleep_ms(35)
            if all_dead:
                break

        clear()
        time.sleep_ms(350)


# ==============================================================================
# Main Demonstration Loop
# ==============================================================================
def main():
    print("=" * 50)
    print("Adafruit 16-LED RGBW NeoPixel Ring Test Starting...")
    print(f"Pin: GP{PIN_NUM} | Pixels: {NUM_PIXELS} | bpp: {BPP} (RGBW)")
    print(f"Brightness: {int(GLOBAL_BRIGHTNESS * 100)}%")
    print("Press Ctrl+C at any time in the REPL to stop.")
    print("=" * 50)

    try:
        # Initial Diagnostic
        test_channels()

        loop_count = 1
        while True:
            print(f"\n--- Demo Cycle {loop_count} ---")

            # 1. Color Wipes (Red, Green, Blue, Pure White)
            print("1. Color Wipe (RGB + White channel)")
            color_wipe((255, 0, 0, 0), wait_ms=30)
            color_wipe((0, 255, 0, 0), wait_ms=30)
            color_wipe((0, 0, 255, 0), wait_ms=30)
            color_wipe((0, 0, 0, 255), wait_ms=30)  # Pure white LED
            color_wipe((0, 0, 0, 0), wait_ms=20)    # Clear wipe
            time.sleep(0.3)

            # 2. Smooth Rainbow Cycle (Sped up)
            print("2. Fast Rainbow Cycle")
            rainbow_cycle(wait_ms=5, loops=3, step=2)
            time.sleep(0.3)

            # 3. Dedicated White Channel Pulse / Breathing
            print("3. Pure White LED Breathing / Pulse")
            white_pulse(wait_ms=15, pulses=2)
            time.sleep(0.3)

            # 4. Spinning Comet Tail (Amber/Gold with white highlight)
            print("4. Comet Tail Spinner")
            comet(color=(255, 100, 0, 80), tail_length=6, wait_ms=35, rotations=4)
            time.sleep(0.3)

            # 5. Dual Counter-Rotating Chasers
            print("5. Dual Counter-Rotating Chasers")
            dual_chasers(wait_ms=45, rotations=8)
            time.sleep(0.3)

            # 6. Explosion Blast & Fallout
            print("6. Detonation & Explosion Fallout")
            explosion(count=1)
            time.sleep(0.5)

            # 7. Fire Kindling & Campfire Flame (starts slowly from embers)
            print("7. Fire Kindling & Flame (slow start)")
            fire(duration_s=8, wait_ms=35, warmup_s=2.5)
            time.sleep(0.3)

            # 8. Theater Chase Marquee
            print("8. Theater Chase (Purple & White)")
            theater_chase((180, 0, 255, 40), wait_ms=75, cycles=6)
            time.sleep(0.3)

            # 9. Warm Sparkle / Twinkle
            print("9. Warm Twinkle Sparkle")
            sparkle((255, 120, 20, 150), sparkles=30, wait_ms=40)
            clear()
            time.sleep(0.5)

            loop_count += 1

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        clear()
        print("NeoPixel Ring cleared. Goodbye!")


if __name__ == "__main__":
    main()
