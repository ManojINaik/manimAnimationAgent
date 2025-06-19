from manim import *

class Scene1_Helper:
    def __init__(self, scene):
        self.scene = scene

    def create_x_axis(self):
        x_axis = NumberLine(
            x_range=[-1, 10, 1],
            length=10,
            include_numbers=True
        ).shift(DOWN * 2)
        return x_axis

    def create_x_label(self, x_axis):
        x_label = MathTex("x").next_to(x_axis, RIGHT, buff=0.3)
        return x_label

    def create_ball(self, x_axis):
        ball = Circle(radius=0.3, color=BLUE, fill_opacity=1).move_to(x_axis.n2p(0))
        return ball

    def create_clock(self):
        clock = Tex("Time: 0.0 s").to_corner(UL).shift(DOWN*0.5 + RIGHT*0.5)
        return clock

    def create_axes(self):
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=4,
            y_length=4
        ).to_corner(UR).shift(DOWN*0.5 + LEFT*0.5)
        return axes

    def create_axes_labels(self, axes):
        x_axis_label = axes.get_x_axis_label("t")
        y_axis_label = axes.get_y_axis_label("x")
        return x_axis_label, y_axis_label

class Scene1(MovingCameraScene):
    def construct(self):
        # Instantiate helper class
        helper = Scene1_Helper(self)

        # Sub-scene 1: Introduction of the x-axis
        x_axis = helper.create_x_axis()
        x_label = helper.create_x_label(x_axis)
        self.play(Create(x_axis), Write(x_label), run_time=2)
        self.wait(0.5)

        # Sub-scene 2: Introduction of the ball and clock
        ball = helper.create_ball(x_axis)
        self.play(FadeIn(ball), run_time=1)
        self.wait(0.3)

        clock = helper.create_clock()
        self.play(FadeIn(clock), run_time=1)
        self.wait(0.3)

        # Sub-scene 3: Motion of the ball and ticking clock
        axes = helper.create_axes()
        x_axis_label, y_axis_label = helper.create_axes_labels(axes)

        self.play(Create(axes), Write(x_axis_label), Write(y_axis_label), run_time=2)

        def position_function(t):
            return t  # Example: constant velocity of 1 unit/second

        graph = axes.plot(position_function, x_range=[0, 0], color=RED)

        def update_ball_position(mob, alpha):
            new_x = x_axis.n2p(position_function(alpha * 8)) #Move ball to x = function(t)
            mob.move_to(new_x)

        def update_graph(mob, alpha):
            new_graph = axes.plot(position_function, x_range=[0, alpha*8], color=RED)
            mob.become(new_graph)

        def update_time(mob, alpha):
            time = alpha * 8
            mob.become(Tex(f"Time: {time:.1f} s").to_corner(UL).shift(DOWN*0.5 + RIGHT*0.5))

        self.play(
            UpdateFromAlphaFunc(ball, update_ball_position),
            UpdateFromAlphaFunc(graph, update_graph),
            UpdateFromAlphaFunc(clock, update_time),
            run_time=8,
            rate_func=linear
        )
        self.wait(1) 