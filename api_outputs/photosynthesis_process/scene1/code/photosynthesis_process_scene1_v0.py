
from manim import *
from manim import config as global_config
from manim_voiceover import VoiceoverScene
from src.utils.elevenlabs_voiceover import get_speech_service # You MUST import like this as this is our custom voiceover service.

# plugins imports, don't change the import statements
# Note: The following plugin imports are commented out due to Python 3.13 compatibility issues
# Uncomment and install individually if needed and compatible with your Python version
# from manim_circuit import *
# from manim_physics import *
# from manim_chemistry import *
# from manim_dsa import *
# from manim_ml import *

# Helper Functions/Classes (Implement and use helper classes and functions for improved code reusability and organization)
class Scene1_Helper:
    """Helper class containing utility functions for scene 1."""
    def __init__(self, scene):
        self.scene = scene

    def create_photosynthesis_text(self):
        """Creates the 'Photosynthesis' Tex object."""
        photosynthesis_text = Tex("Photosynthesis", color=BLUE)
        photosynthesis_text.to_edge(UP, buff=0.7)  # Position at top, respecting margin
        return photosynthesis_text

    def create_explanation_text(self):
        """Creates the explanation Tex object."""
        explanation_text = Tex("Plants make their own food!", color=YELLOW)
        explanation_text.next_to(self.create_photosynthesis_text(), DOWN, buff=0.3)  # Respect spacing
        return explanation_text

class Scene1(VoiceoverScene, MovingCameraScene):
    """Introduction scene explaining photosynthesis."""
    def construct(self):
        # Initialize speech service
        self.set_speech_service(get_speech_service())

        # Instantiate helper class
        helper = Scene1_Helper(self)

        # --- Stage 1: Ecosystem Overview ---
        with self.voiceover(text="Life on Earth thrives in diverse ecosystems, from lush forests to vibrant oceans.") as tracker:
            # Create an ImageMobject of a vibrant forest ecosystem
            image = ImageMobject("forest_ecosystem.jpg")  # Replace with actual path
            image.height = 7
            image.width = 12
            image.move_to(ORIGIN)
            self.play(FadeIn(image), run_time=tracker.duration)
            self.wait(2)

        # --- Stage 2: Zooming into a Plant ---
        with self.voiceover(text="And at the heart of almost every ecosystem, we find plants.") as tracker:
            # Identify a plant within the image to focus on.
            plant_location = [-2, -1, 0]  # Example location. Adjust as needed.
            self.play(
                self.camera.frame.animate.move_to(plant_location).scale(0.5), run_time=tracker.duration
            )
            self.wait(2)

        # --- Stage 3: Zooming into a Cell ---
        with self.voiceover(text="But have you ever wondered how plants get their energy?") as tracker:
            self.wait(3)
        with self.voiceover(text="Like all living things, plants need energy to grow and survive.") as tracker:
            self.wait(3)
        with self.voiceover(text="And just like our bodies are made of cells, so are plants! This process happens inside each of these tiny compartments.") as tracker:
            # Create a Circle to represent a plant cell.
            cell = Circle(radius=1, color=GREEN)
            self.play(Transform(image, cell.move_to(ORIGIN)), run_time=tracker.duration)
            self.play(
                self.camera.frame.animate.move_to(ORIGIN).scale(0.2), run_time=tracker.duration
            )
            self.wait(2)

        # --- Stage 4: Introducing Photosynthesis ---
        with self.voiceover(text="Plants use a remarkable process called...") as tracker:
            self.wait(2)
        with self.voiceover(text="...Photosynthesis!") as tracker:
            # Create a Tex object to introduce photosynthesis.
            photosynthesis_text = helper.create_photosynthesis_text()
            self.play(FadeIn(photosynthesis_text), run_time=tracker.duration)

            # Create a Tex object to briefly explain photosynthesis.
            explanation_text = helper.create_explanation_text()
            self.play(Write(explanation_text), run_time=tracker.duration)
            self.wait(3)

        # --- Stage 5: Scene End ---
        with self.voiceover(text="Simply put, Photosynthesis is how plants make their own food!") as tracker:
            self.wait(3)
        with self.voiceover(text="In the next scene, we'll explore the specifics of this fascinating process.") as tracker:
            self.play(FadeOut(photosynthesis_text, explanation_text), run_time=tracker.duration)
            self.wait(1)
