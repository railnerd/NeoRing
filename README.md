# Adafruit 16-LED RGBW NeoPixel Ring — MicroPython Test Suite

This project contains a comprehensive MicroPython test program and visual effects suite for the **Adafruit 16-LED RGBW NeoPixel Ring** (e.g., Cool White, Warm White, or Natural White variants).

---

## 1. Wiring Guide

| NeoPixel Ring Pin | Microcontroller (Pico / ESP32) | Notes |
| :--- | :--- | :--- |
| **GND** | **GND** | Common ground with microcontroller |
| **PWR / 5V / VDC** | **VBUS (5V)** or external 5V power supply | 16 RGBW LEDs at 100% white can draw up to ~0.9A. For USB power, keep brightness low (<30%). |
| **Data In (DI / DIN)** | **GPIO Pin** (e.g., GP0 on Pico, GPIO 4 on ESP32) | Connect via a 300–500 Ω resistor if available to protect the first data pin. |

> [!TIP]
> **Power Tip:** When powering directly from a microcontroller's USB VBUS/5V pin, keep `GLOBAL_BRIGHTNESS` around `0.2`–`0.3` to avoid exceeding USB port current limits. For full brightness, use an external 5V 1A–2A power supply and add a 1000 µF capacitor across +5V and GND.

---

## 2. Key RGBW Differences in MicroPython

Unlike standard RGB NeoPixels (which use 3 bytes per pixel), RGBW NeoPixels feature a dedicated fourth LED element (White):

1. **`bpp=4` parameter:**  
   When instantiating the `neopixel.NeoPixel` object, specify `bpp=4`:
   ```python
   np = neopixel.NeoPixel(Pin(PIN_NUM, Pin.OUT), 16, bpp=4)
   ```
2. **4-Tuple Colors:**  
   Every color is represented as `(Red, Green, Blue, White)` where each channel is `0–255`:
   - `(255, 0, 0, 0)` &rarr; Pure Red
   - `(0, 255, 0, 0)` &rarr; Pure Green
   - `(0, 0, 255, 0)` &rarr; Pure Blue
   - `(0, 0, 0, 255)` &rarr; Pure Dedicated White (cleanest, most power-efficient white)
   - `(255, 120, 0, 100)` &rarr; Warm Amber + White tint

---

## 3. Included Effects

The test program in [`main.py`](file:///Users/dave/Documents/NeoRing/main.py) cycles through the following visual routines:

1. **`test_channels()`**: Sequential test of individual channels (Red &rarr; Green &rarr; Blue &rarr; White) to verify wiring and color order.
2. **`color_wipe()`**: Progressive single-pixel wipe around the ring in multiple colors.
3. **`rainbow_cycle()`**: Smooth 360° hue gradient rotation.
4. **`white_pulse()`**: Breathing / pulsing effect using the dedicated white channel.
5. **`comet()`**: Rotating spinner head with an exponential fading tail (calibrated to ~2.2s).
6. **`dual_chasers()`**: Two counter-rotating heads (RGB blue & white) that blend when colliding (~5.8s).
7. **`explosion()`**: Multi-stage detonation: accelerating fuse spark &rarr; blinding white-hot flash &rarr; expanding fireball &rarr; scattered glowing embers cooling from yellow to red to dark with occasional crackles.
8. **`fire()`**: Campfire / flame effect that slowly kindles from faint embers, spreads thermally across neighboring LEDs, grows into a roaring fire with white-hot flare-ups, and smoothly dies down (~8s).
9. **`theater_chase()`**: Marquee crawling dot pattern.
10. **`sparkle()`**: Random twinkle across the ring.

---

## 4. How to Run

### Using Thonny IDE (Recommended)
1. Connect your MicroPython board via USB.
2. Open **Thonny IDE** and select the MicroPython interpreter (bottom right corner).
3. Open [`main.py`](file:///Users/dave/Documents/NeoRing/main.py).
4. Adjust `PIN_NUM` at the top of the file if you are using a different GPIO pin.
5. Click the green **Run current script (F5)** button.
6. Press `Ctrl + C` in the Shell / REPL to stop the program and clear the LEDs.

### Using `mpremote` (CLI)
```bash
mpremote run main.py
```
