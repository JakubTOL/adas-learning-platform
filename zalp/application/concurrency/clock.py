"""
Clock source for the application layer.
using Kivy Clock for easy integration.

# TODO: Even if we can import the clock properly without Kivy starting,
#       the clock itself won't progress, because it's the Kivy App object that calls
#       the tick() method of the clock.
#       Implement a way to make the application schedule properly even without GUI
#       (headless mode).
"""

from kivy.clock import Clock

__all__ = ['Clock']
