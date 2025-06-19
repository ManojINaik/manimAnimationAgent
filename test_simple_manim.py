from manim import *

class SimpleTest(Scene):
    def construct(self):
        # Create a simple circle and move it
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))
        self.play(circle.animate.shift(RIGHT * 2))
        self.wait(1) 