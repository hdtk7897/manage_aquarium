#basic example of using the Pi5Neo class to control a NeoPixel strip
from pi5neo import Pi5Neo  # Import the Pi5Neo class
import time

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
    """Set the entire strip to a solid color and hold for a duration"""
    neo.fill_strip(red, green, blue)
    neo.update_strip()
    time.sleep(duration)

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
    for color in rainbow_colors:
        neo.fill_strip(*color)
        neo.update_strip()
        time.sleep(delay)

def main(hour):

    # Initialize the Pi5Neo class with 10 LEDs
    pi5_neo = Pi5Neo('/dev/spidev0.0', 60, 800)

    # Run demo functions
    # demo_solid_color(pi5_neo, 5, 5, 5)  # Red strip
    demo_solid_color(pi5_neo, *hour_light[hour])  # Red strip
    # demo_rainbow_cycle(pi5_neo)  # Rainbow cycle effect

