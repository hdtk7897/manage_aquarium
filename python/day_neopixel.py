"""Day neopixel demo with robust SPI detection and graceful fallback.

This script will try to locate a /dev/spidev* device, initialize the
Pi5Neo controller if available, and run simple demo effects. If SPI is
not available the functions become no-ops and print informative messages.
"""

import time
import glob
import os
import logging

try:
    from pi5neo import Pi5Neo  # type: ignore
except Exception:
    Pi5Neo = None

hour_light = [
    [0,0,0], #0
    [0,0,0], #1
    [0,0,0], #2
    [0,0,0], #3
    [10,2,2], #4
    [20,5,5], #5
    [40,10,10], #6
    [50,20,20], #7
    [100,50,50], #8
    [150,150,150], #9
    [180,180,180], #10
    [200,200,200], #11
    [200,200,200], #12
    [200,200,200], #13
    [200,200,200], #14
    [150,150,150], #15
    [100,100,100], #16
    [50,10,10], #17
    [10,5,5], #18
    [10,5,5], #19
    [5,2,2], #20
    [0,0,0], #21
    [0,0,0], #22
    [0,0,0], #23
]

def demo_solid_color(neo, red, green, blue, duration=2):
    """Set the entire strip to a solid color and hold for a duration.

    If `neo` is None this is a no-op (prints info) so scripts can run
    on machines without SPI (development machines, CI, etc.).
    """
    if neo is None:
        logging.info("Neo strip disabled: skipping solid color %s,%s,%s", red, green, blue)
        time.sleep(duration)
        return

    try:
        neo.fill_strip(red, green, blue)
        neo.update_strip()
        time.sleep(duration)
    except OSError as e:
        logging.warning("SPI error updating neopixel: %s", e)
    except Exception as e:
        logging.exception("Unexpected error updating neopixel: %s", e)

def demo_rainbow_cycle(neo, delay=0.1):
    """Cycle through rainbow colors on the entire strip"""
    rainbow_colors = [
        (255, 0, 0),  # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (75, 0, 130),  # Indigo
        (148, 0, 211)  # Violet
    ]
    if neo is None:
        logging.info("Neo strip disabled: skipping rainbow cycle")
        return

    for color in rainbow_colors:
        try:
            neo.fill_strip(*color)
            neo.update_strip()
            time.sleep(delay)
        except Exception:
            logging.exception("Error while running rainbow cycle")

def find_spidev_device():
    """Return the first matching /dev/spidev* path or None."""
    devices = sorted(glob.glob("/dev/spidev*"))
    return devices[0] if devices else None


def init_pi5neo(num_leds=60, spi_speed=800):
    """Try to initialize Pi5Neo using the first available spidev device.

    Returns a Pi5Neo instance or None on failure.
    """
    if Pi5Neo is None:
        logging.info("pi5neo module not available; neopixel disabled")
        return None

    path = find_spidev_device()
    if not path:
        logging.info("No /dev/spidev device found; neopixel disabled")
        return None

    try:
        # Pi5Neo expects path, number of LEDs, and speed (khz?)
        neo = Pi5Neo(path, num_leds, spi_speed)
        logging.info("Initialized Pi5Neo on %s (leds=%s speed=%s)", path, num_leds, spi_speed)
        return neo
    except FileNotFoundError as e:
        logging.warning("Failed to open SPI device %s: %s", path, e)
    except OSError as e:
        logging.warning("SPI initialization error for %s: %s", path, e)
    except Exception as e:
        logging.exception("Unexpected error initializing Pi5Neo: %s", e)
    return None


def main(hour):
    logging.basicConfig(level=logging.INFO)

    pi5_neo = init_pi5neo(num_leds=60, spi_speed=800)

    # Run demo functions
    demo_solid_color(pi5_neo, *hour_light[hour])
    # demo_rainbow_cycle(pi5_neo)


if __name__ == "__main__":
    import datetime
    now = datetime.datetime.now()
    main(now.hour)

