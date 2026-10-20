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

def test_channels(hold_ms=250):
    """Diagnostic check: quickly cycle through Red, Green, Blue, and White channels."""
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
        time.sleep_ms(hold_ms)
    clear()
    time.sleep_ms(150)


def color_wipe(color, wait_ms=15):
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


def welding_shop(duration_s=10, ambient_shop=True):
    """
    Simulates an electric arc welder operating inside a workshop:
    1. Ambient Shop Light: Low overhead workshop illumination (soft warm/neutral white).
    2. Striking the Arc: Tap/scratch ignition attempts with quick, sharp flash pops.
    3. Continuous Weld Bead: Fierce, high-frequency electric arc flicker (cyan/blue-white),
       with ambient reflections bouncing off the shop walls and flying molten sparks/spatter.
    4. Slag & Puddle Glow: Hot molten seam remaining orange/red and slowly cooling
       through cherry-red embers after the arc cuts out.
    5. Natural Intermittent Work: Alternates between passes, tacks, and cooling intervals.
    """
    start_time = time.ticks_ms()
    total_ms = int(duration_s * 1000)
    ambient_color = (12, 10, 6, 20) if ambient_shop else (0, 0, 0, 0)
    arc_brightness = min(1.0, GLOBAL_BRIGHTNESS * 1.6)

    def draw_ambient():
        for i in range(NUM_PIXELS):
            set_pixel(i, ambient_color)
        np.write()

    draw_ambient()
    time.sleep_ms(350)

    weld_pos = random.randint(0, NUM_PIXELS - 1)

    while time.ticks_diff(time.ticks_ms(), start_time) < total_ms:
        # Phase 1: Striking the Arc / Tacking (quick strike & short pauses)
        strikes = random.randint(2, 4)
        for _ in range(strikes):
            if time.ticks_diff(time.ticks_ms(), start_time) >= total_ms:
                break
            # Strike flash
            draw_ambient()
            set_pixel(weld_pos, (120, 190, 255, 255), brightness=arc_brightness)
            if random.random() < 0.5:
                # Slight adjacent bounce
                set_pixel((weld_pos + 1) % NUM_PIXELS, (30, 60, 120, 80))
            np.write()
            time.sleep_ms(random.randint(15, 35))

            # Pause between strikes
            draw_ambient()
            time.sleep_ms(random.randint(50, 140))

        if time.ticks_diff(time.ticks_ms(), start_time) >= total_ms:
            break

        # Phase 2: Continuous Weld Bead (High-frequency arc jitter, wall reflections & spatter)
        bead_duration_ms = random.randint(1400, 2800)
        bead_start = time.ticks_ms()

        while (time.ticks_diff(time.ticks_ms(), bead_start) < bead_duration_ms and
               time.ticks_diff(time.ticks_ms(), start_time) < total_ms):

            # Occasional micro-stutter / gap in arc transfer
            if random.random() < 0.08:
                draw_ambient()
                # Brief molten pool glimpse
                set_pixel(weld_pos, (255, 80, 0, 30))
                np.write()
                time.sleep_ms(random.randint(15, 30))
                continue

            # Arc intensity and color fluctuation
            arc_intensity = random.randint(180, 255)
            arc_col = (
                random.randint(70, 140),
                random.randint(150, 230),
                255,
                arc_intensity
            )

            # Shop wall reflections based on arc intensity
            flash_refl = random.randint(15, 50)
            for i in range(NUM_PIXELS):
                d = min(abs(i - weld_pos), NUM_PIXELS - abs(i - weld_pos))
                bounce = max(0, int(flash_refl / (1.0 + d * 0.45)))
                refl_color = (
                    min(255, ambient_color[0] + int(bounce * 0.3)),
                    min(255, ambient_color[1] + int(bounce * 0.5)),
                    min(255, ambient_color[2] + int(bounce * 0.8)),
                    min(255, ambient_color[3] + bounce),
                )
                set_pixel(i, refl_color)

            # Weld site: intense electric arc
            set_pixel(weld_pos, arc_col, brightness=arc_brightness)

            # Molten halo on neighboring pixel
            side_pixel = (weld_pos + random.choice([-1, 1])) % NUM_PIXELS
            set_pixel(side_pixel, (200, 120, 100, int(arc_intensity * 0.6)), brightness=arc_brightness)

            # Flying sparks / spatter bouncing across the workshop
            if random.random() < 0.28:
                spk_idx = (weld_pos + random.randint(2, NUM_PIXELS - 2)) % NUM_PIXELS
                spark_col = (255, random.randint(160, 220), random.randint(20, 60), random.randint(100, 220))
                set_pixel(spk_idx, spark_col, brightness=arc_brightness)

            np.write()
            time.sleep_ms(random.randint(15, 35))

            # Slow seam progression
            if random.random() < 0.05:
                weld_pos = (weld_pos + random.choice([-1, 1])) % NUM_PIXELS

        # Phase 3: Arc Cut-Off & Molten Puddle / Slag Cooling
        cooling_steps = random.randint(20, 28)
        for step in range(cooling_steps):
            if time.ticks_diff(time.ticks_ms(), start_time) >= total_ms:
                break
            heat = int(255 * (1.0 - (step / cooling_steps) ** 1.3))
            draw_ambient()
            if heat > 160:
                puddle_col = (255, int(heat * 0.55), 0, int((heat - 160) * 0.7))
            elif heat > 65:
                puddle_col = (int(heat * 1.3), int(heat * 0.2), 0, 0)
            elif heat > 15:
                puddle_col = (int(heat * 0.8), 0, 0, 0)
            else:
                puddle_col = ambient_color
            set_pixel(weld_pos, puddle_col)

            # Faint edge warmth
            if heat > 90:
                side_p = (weld_pos + 1) % NUM_PIXELS
                set_pixel(side_p, (int(heat * 0.45), int(heat * 0.08), 0, 0))

            np.write()
            time.sleep_ms(40)

        # Phase 4: Welder pause / reposition before next pass
        draw_ambient()
        pause_ms = random.randint(400, 900)
        time.sleep_ms(pause_ms)
        weld_pos = (weld_pos + random.randint(2, 6)) % NUM_PIXELS

    clear()


def radioactive_lab(duration_s=10, ambient_lab=True):
    """
    Simulates a high-containment radioactive research laboratory:
    1. Clinical Lab Ambient: Cold, sterile fluorescent background (cool-teal & white tint).
    2. Isotope Core: Slowly breathing toxic neon-green / uranium-lime containment vessel.
    3. Cherenkov Radiation: Periodic criticality surges in piercing electric cyan-blue.
    4. Geiger Counter Scintillations: Random ionizing particle hits flashing brightly.
    5. Containment Hazard Beacon: Rhythmic amber warning strobe on the perimeter.
    """
    start_time = time.ticks_ms()
    total_ms = int(duration_s * 1000)

    # Core containment pixels (bottom arc of the ring)
    core_pixels = [6, 7, 8, 9, 10]
    # Warning hazard strobes (top of the ring)
    hazard_pixels = [0, 1]

    # Precalculated sine-like breathing table (0.0 to 1.0)
    pulse_lut = [
        0.30, 0.35, 0.45, 0.60, 0.78, 0.92, 1.00, 0.95,
        0.82, 0.65, 0.48, 0.36, 0.28, 0.25, 0.24, 0.26
    ]
    lut_len = len(pulse_lut)

    step = 0
    cherenkov_active = False
    cherenkov_timer = time.ticks_ms()
    cherenkov_start = 0
    cherenkov_duration = 1400

    while time.ticks_diff(time.ticks_ms(), start_time) < total_ms:
        now = time.ticks_ms()

        # Trigger a Cherenkov criticality surge every 3.5 - 5 seconds
        if not cherenkov_active and time.ticks_diff(now, cherenkov_timer) > 3500:
            cherenkov_active = True
            cherenkov_start = now
            cherenkov_duration = random.randint(1200, 1600)

        # 1. Base sterile clinical lab background
        lab_ambient = (0, 8, 12, 14) if ambient_lab else (0, 0, 0, 0)
        for i in range(NUM_PIXELS):
            set_pixel(i, lab_ambient)

        # Pulse breathing factor for the isotope core
        pulse = pulse_lut[step % lut_len]

        # 2. Containment Core State
        if cherenkov_active:
            c_elapsed = time.ticks_diff(now, cherenkov_start)
            if c_elapsed >= cherenkov_duration:
                cherenkov_active = False
                cherenkov_timer = now
                c_factor = 0.0
            else:
                progress = c_elapsed / cherenkov_duration
                c_factor = 1.0 - abs(progress - 0.5) * 2.0  # 0 -> 1 -> 0

            # Cherenkov radiation surge: electric cyan-blue glow
            c_blue = int(255 * c_factor)
            c_cyan = int(190 * c_factor)
            c_white = int(80 * c_factor)

            for cp in core_pixels:
                set_pixel(cp, (0, c_cyan, c_blue, c_white))

            # Radiation wave rippling to neighboring containment sectors
            for cp in [4, 5, 11, 12]:
                spread = int(c_factor * 130)
                set_pixel(cp, (0, int(spread * 0.7), spread, int(spread * 0.35)))
        else:
            # Normal radioactive isotope glow (toxic uranium / lime green)
            r_val = int(25 * pulse)
            g_val = int(140 + 115 * pulse)
            b_val = int(10 * (1.0 - pulse))
            w_val = int(20 * pulse)

            for cp in core_pixels:
                intensity = 1.0 if cp == 8 else (0.8 if cp in (7, 9) else 0.55)
                col = (
                    int(r_val * intensity),
                    int(g_val * intensity),
                    int(b_val * intensity),
                    int(w_val * intensity)
                )
                set_pixel(cp, col)

        # 3. Containment Hazard Warning Beacon (Amber pulse on top LEDs)
        hazard_phase = (step // 4) % 4
        if hazard_phase == 0:
            for hp in hazard_pixels:
                set_pixel(hp, (255, 90, 0, 0))
        else:
            for hp in hazard_pixels:
                set_pixel(hp, (15, 5, 0, 0))

        # 4. Geiger Counter Scintillations (Erratic ionizing particle hits)
        scint_chance = 0.45 if cherenkov_active else 0.18
        if random.random() < scint_chance:
            spark_p = random.randint(0, NUM_PIXELS - 1)
            if cherenkov_active:
                spark_col = (100, 220, 255, 255)  # Ionized blue-white flash
            else:
                spark_col = (80, 255, 100, 220)   # Fluorescing green-white pop
            set_pixel(spark_p, spark_col, brightness=min(1.0, GLOBAL_BRIGHTNESS * 1.5))

        np.write()
        time.sleep_ms(35)
        step += 1

    clear()


def concert_hall(duration_s=12):
    """
    Simulates a dynamic concert hall / arena stage interior lighting show:
    1. House Lights Dimming: Grand amber/warm-white chandelier lights dimming smoothly.
    2. Theatrical Stage Wash: Saturated background stage washes with rhythmic musical beat pulses.
    3. Moving Automated Beams: Dual counter-rotating moving head fixtures sweeping the auditorium.
    4. Center Followspot: Crisp pure-white spotlight tracking the lead performer on stage.
    5. Crowd Audience Blinders: Blinding 3200K tungsten amber-white flashes on musical drops.
    6. Curtain Call / Encore: Warm house illumination returning for applause.
    """
    start_time = time.ticks_ms()
    total_ms = int(duration_s * 1000)

    # 1. House Lights Fade Down (Chandeliers dimming as performance starts)
    house_color = (200, 100, 15, 120)
    for step in range(20, -1, -1):
        factor = step / 20.0
        scaled_house = tuple(int(c * factor) for c in house_color)
        fill(scaled_house)
        time.sleep_ms(30)
        if time.ticks_diff(time.ticks_ms(), start_time) >= total_ms:
            clear()
            return

    # 2. Show Phase: Sweeping automated movers, followspots, beat washes & blinders
    theatrical_palettes = [
        # (Wash color, Beam 1 color, Beam 2 color)
        ((15, 0, 40, 0),    (255, 0, 140, 20),   (0, 200, 255, 40)),    # Violet wash + Magenta & Cyan beams
        ((30, 10, 0, 5),    (255, 180, 0, 50),   (0, 120, 255, 80)),    # Warm wash + Gold & Azure beams
        ((0, 20, 30, 0),    (0, 255, 160, 20),   (255, 0, 80, 20)),     # Teal wash + Emerald & Rose beams
    ]

    palette_idx = 0
    beam1_pos = 0.0
    beam2_pos = 8.0
    followspot_pos = 4.0
    followspot_dir = 0.15

    last_beat = time.ticks_ms()
    beat_interval_ms = 450  # ~133 BPM concert tempo

    while time.ticks_diff(time.ticks_ms(), start_time) < (total_ms - 1000):
        now = time.ticks_ms()

        # Check musical beat pulse
        is_beat = False
        if time.ticks_diff(now, last_beat) >= beat_interval_ms:
            last_beat = now
            is_beat = True
            # Transition lighting palette on musical phrases
            if random.random() < 0.2:
                palette_idx = (palette_idx + 1) % len(theatrical_palettes)

        wash_col, b1_col, b2_col = theatrical_palettes[palette_idx]

        # Crowd blinder flash on major musical accent
        if is_beat and random.random() < 0.15:
            # Full arena blinder flash (Tungsten Warm White + Amber)
            fill((255, 200, 80, 255), brightness=min(1.0, GLOBAL_BRIGHTNESS * 1.5))
            time.sleep_ms(45)
            continue

        # Render stage background wash with musical pulse boost
        wash_boost = 1.8 if is_beat else 1.0
        active_wash = tuple(min(255, int(c * wash_boost)) for c in wash_col)
        for i in range(NUM_PIXELS):
            set_pixel(i, active_wash)

        # Update moving head beam positions
        beam1_pos = (beam1_pos + 0.35) % NUM_PIXELS
        beam2_pos = (beam2_pos - 0.40) % NUM_PIXELS

        # Followspot gently tracking across the performer stage
        followspot_pos += followspot_dir
        if followspot_pos > 11.0 or followspot_pos < 3.0:
            followspot_dir = -followspot_dir

        # Draw Beam 1 (Moving automated profile fixture)
        b1_idx = int(beam1_pos)
        set_pixel(b1_idx, b1_col)
        set_pixel((b1_idx + 1) % NUM_PIXELS, tuple(int(c * 0.4) for c in b1_col))

        # Draw Beam 2 (Counter-rotating automated beam fixture)
        b2_idx = int(beam2_pos)
        set_pixel(b2_idx, b2_col)
        set_pixel((b2_idx - 1) % NUM_PIXELS, tuple(int(c * 0.4) for c in b2_col))

        # Draw Center Followspot (Crisp pure-white beam)
        f_idx = int(followspot_pos)
        set_pixel(f_idx, (0, 0, 0, 255), brightness=min(1.0, GLOBAL_BRIGHTNESS * 1.4))

        np.write()
        time.sleep_ms(30)

    # 3. Curtain Call / House Lights return for applause
    for step in range(0, 16):
        factor = step / 15.0
        scaled_house = tuple(int(c * factor) for c in house_color)
        fill(scaled_house)
        time.sleep_ms(35)

    time.sleep_ms(300)
    clear()


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

            # 1. Color Wipes (Red, Green, Blue, Pure White) - Sped up
            print("1. Fast Color Wipe (RGB + White channel)")
            color_wipe((255, 0, 0, 0), wait_ms=12)
            color_wipe((0, 255, 0, 0), wait_ms=12)
            color_wipe((0, 0, 255, 0), wait_ms=12)
            color_wipe((0, 0, 0, 255), wait_ms=12)  # Pure white LED
            color_wipe((0, 0, 0, 0), wait_ms=8)     # Clear wipe
            time.sleep(0.15)

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
            time.sleep(1.8)

            # 10. Welding Inside a Shop (Arc Strikes, Wall Bounce & Cooling Puddle)
            print("10. Welding Inside a Shop")
            welding_shop(duration_s=10, ambient_shop=True)
            clear()
            time.sleep(1.8)

            # 11. Radioactive Lab Interior (Isotope Core, Cherenkov Surges & Geiger Clicks)
            print("11. Radioactive Lab Interior")
            radioactive_lab(duration_s=10, ambient_lab=True)
            clear()
            time.sleep(1.8)

            # 12. Concert Hall Lighting (House Dim, Moving Beams, Followspot & Blinders)
            print("12. Concert Hall Stage Lighting")
            concert_hall(duration_s=12)
            clear()
            time.sleep(1.8)

            loop_count += 1

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        clear()
        print("NeoPixel Ring cleared. Goodbye!")


if __name__ == "__main__":
    main()
