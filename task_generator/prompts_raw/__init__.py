# This file is generated automatically through parse_prompt.py

_prompt_context_learning_scene_plan = """Here are some example scene plans to help guide your scene planning:

{examples}

Please follow a similar structure while maintaining creativity and relevance to the current topic."""

_prompt_scene_vision_storyboard = """You are an expert in educational video production and Manim animation.
**Reminder:** Each scene's vision and storyboard plan is entirely self-contained. There is no dependency on any implementation from previous or subsequent scenes. However, the narration will treat all scenes as part of a single, continuous video.

Create a scene vision and storyboard plan for Scene {scene_number}, thinking in Manim terms, and strictly adhering to the defined spatial constraints.

Topic: {topic}
Description: {description}

Scene Overview:
{scene_outline}

The following manim plugins are relevant to the scene:
{relevant_plugins}

**Spatial Constraints (Strictly Enforced):**
*   **Safe area margins:** 0.5 units on all sides from the scene edges. *All objects must be positioned within these margins.*
*   **Minimum spacing:** 0.3 units between any two Manim objects (measured edge to edge). *Ensure a minimum spacing of 0.3 units to prevent overlaps and maintain visual clarity. This spacing must be maintained between all objects in the scene, including text, shapes, and graphs.*

**Positioning Requirements:**
1.  Safe area margins (0.5 units).
2.  Minimum spacing between objects (0.3 units).
3.  Relative positioning (`next_to`, `align_to`, `shift`) from `ORIGIN`, margins, or object references. **No absolute coordinates are allowed.** All positioning MUST be relative and clearly specified using reference points and relative positioning methods.
4.  Transition buffers (`Wait` times) between sub-scenes and animation steps for visual clarity and pacing.

**Diagrams/Sketches (Optional but Recommended for Complex Scenes):**
*   For complex scenes, consider including a simple diagram or sketch (even text-based) of the intended layout to visually clarify spatial relationships and ensure adherence to spacing and margin constraints.

**Focus:**
*   Focus on clear visual communication of the scene's learning objective through effective use of Manim objects and animations, while strictly adhering to the defined spatial constraints.
*   Provide detailed visual descriptions in Manim terms to guide human implementation.
*   Prioritize explanation and visualization of the theorem. Do not include any promotional elements or quiz sessions.
*   Minimize text usage - rely primarily on visual elements, mathematical notation, and animations to convey concepts. Use text sparingly and only when necessary for clarity.

**Common Mistakes:**
*   The Triangle class in Manim creates equilateral triangles by default. To create a right-angled triangle, use the Polygon class instead.

**Manim Plugins:**
*   Consider using established Manim plugins if they significantly simplify the implementation or offer visual elements not readily available in core Manim.  If a plugin is used, clearly indicate this in the storyboard with a note like "**Plugin Suggestion:** Consider using the `manim-plugin-name` plugin for [brief explanation of benefit]."

You MUST generate the scene vision and storyboard plan for the scene in the following format (from ```xml to </SCENE_VISION_STORYBOARD_PLAN>```):

```xml
<SCENE_VISION_STORYBOARD_PLAN>
[SCENE_VISION]
1.  **Scene Overview**:
    - Scene story, key takeaway, video role. *Consider how this scene fits within the overall video narrative.*
    - **Visual learning objectives for viewers:** Think about *specific Manim object types* that best represent the learning objective. Example: "Visualize roots as `Dot` objects on an `Axes` graph." Be specific about Manim object classes (e.g., `MathTex`, `Shapes`, `Graphs`, `Axes`, `VGroup`).  If a plugin provides a relevant object type, mention it (e.g., "Visualize X using `PluginObject` from `manim-plugin-name`").
    - How Manim visuals & animations support learning? Consider `MathTex`, `Shapes`, `Graphs`, `Axes`, `VGroup`. Focus on spatial arrangement and clarity, ensuring adherence to safe area margins and minimum spacing (0.3 units). Consider using `VGroup` to group related formula components for easier animation and spatial control. Example: "Use `VGroup` to group related formula components for easier animation and spatial control, ensuring a minimum spacing of 0.3 units between VGroup and other scene elements."  If a plugin offers a more efficient way to achieve a visual effect, mention it.
    - Key concepts to emphasize visually using visual hierarchy and spatial arrangement in Manim, while respecting safe area margins and minimum spacing (0.3 units).  **Use `MathTex` for mathematical expressions and equations. Use `Tex` for general text, titles, labels, and any non-mathematical text. When mixing text with mathematical symbols in `MathTex`, use the `\\text{{}}` command (e.g., `MathTex(r"\\text{{Area}} = \\pi r^2")`)**

[STORYBOARD]
1.  **Visual Flow & Pacing (Manim Animation Sequence)**:
    - Describe the sequence of Manim visuals and animations (`Text`, `Circle`, `Arrow`, `Create`, `FadeIn`, `Transform`, etc.). Be specific about animation types and their parameters (e.g., `run_time`).  If a plugin provides a specific animation type, mention it (e.g., "Use `PluginAnimation` from `manim-plugin-name`").
    - Key visual moments: composition and arrangement of Manim elements, ensuring all elements are within safe area margins and maintain a minimum 0.3 unit spacing. Example: "`MathTex` formula center (`.move_to(ORIGIN)`) with `Write` animation, ensuring 0.3 unit spacing from scene edges and other elements."
    - Visual transitions between ideas using Manim animations (`Transform`, `Shift`, `FadeOutAndShift`, etc.). Specify transition animations and their timings.
    - Scene pacing (pauses, action) and Manim animation timing's role. Use `Wait()` for transition buffers and visual clarity.
    - **Sub-scene Breakdown**: Divide the scene into logical sub-scenes, each focusing on a specific step in the explanation or visualization.
        - For each sub-scene, start with a **Visual Element**: The primary visual component that drives the explanation (e.g., mathematical notation, diagram, graph).  If this element comes from a plugin, clearly state this (e.g., "Visual Element: `PluginObject` from `manim-plugin-name`").
        - Detail the **Animation Sequence**: Describe step-by-step the Manim animations and visual elements for each sub-scene. Be specific about:
            - **Text Usage Guidelines:**
                - **Use `MathTex` *only* for mathematical expressions and equations.**
                - **Use `Tex` for all other text, including labels, explanations, and titles.**
                - **When mixing text with mathematical symbols in `MathTex`, wrap the text portions in `\\text{{}}`. Example: `MathTex(r"\\text{{Area of circle}} = \\pi r^2")`.**
            - Manim object classes (`MathTex`, `Circle`, `Arrow`, `Axes`, `Plot`, `Line`, `VGroup`, etc.), prioritizing mathematical notation and visual elements over text.  Include plugin object classes where appropriate.
            - Animation types (`Create`, `Write`, `FadeIn`, `Transform`, `FadeOut`, `Circumscribe`, `FocusOn`, etc.) and their parameters (e.g., `run_time`). Include plugin animation types where appropriate.
            - Positioning of objects using relative positioning methods (`.next_to()`, `.align_to()`, `.shift()`, `.to_corner()`, `.move_to(ORIGIN)`, etc.) and references to other objects or scene elements. **No absolute coordinates allowed.**
            - Color and style specifications (e.g., `color=BLUE`, `stroke_width=2`, `dashed=True`).
            - Explicitly mention safe area margins and minimum spacing (0.3 units) for all objects within each sub-scene.

</SCENE_VISION_STORYBOARD_PLAN>
```"""

_prompt_rag_query_generation_storyboard = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to transform a storyboard plan for a Manim video scene into effective queries that will retrieve relevant information from Manim documentation. The storyboard plan describes the scene's visual elements and narrative flow.

Here is the storyboard plan:

{storyboard}

Based on the storyboard plan, generate multiple human-like queries (maximum 10) for retrieving relevant documentation. Please ensure that the search targets are different so that the RAG can retrieve a diverse set of documents covering various aspects of the implementation.

**Specifically, ensure that:**
1.  At least some queries are focused on retrieving information about **Manim core functionalities**, like general visual elements or animations. Frame these queries using Manim terminology (classes, methods, concepts).
2.  If the storyboard suggests using specific visual effects or complex animations that might be plugin-related, include at least 1 query specifically targeting **plugin documentation**.  Make sure to mention the plugin name if known or suspected.
3.  Queries should be general enough to explore different possibilities within Manim and its plugins based on the storyboard's visual and narrative descriptions, but also specific enough to target Manim documentation effectively.

The above storyboard might be relevant to these plugins: {relevant_plugins}.
Note that you MUST NOT use the plugins that are not listed above.

Output the queries in the following format:
```json
[
    {{"query": "content of query 1", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 2", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 3", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 4", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 5", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 6", "type": "manim_core/{relevant_plugins}"}},
    {{"query": "content of query 7", "type": "manim_core/{relevant_plugins}"}},
]
``` """

_code_background = """PLEASE DO NOT create another color background Rectangles. Default background (Black) is enough.
PLEASE DO NOT use BLACK color for any text.
"""

_prompt_context_learning_vision_storyboard = """Here are some example vision and storyboard plans to help guide your planning:

{examples}

Please follow a similar structure while maintaining creativity and relevance to the current scene."""

_prompt_context_learning_code = """Here are some example Manim code implementations to help guide your code generation:

{examples}

Please follow similar patterns and best practices while implementing the current scene."""

_code_limit = """Note that the frame width and height are 14.222222222222221 and 8.0 respectively. And the center of the frame is (0, 0, 0).
It means to avoid putting any object out of the frame, you should limit the x and y coordinates of the objects.
limit x to be within -7.0 and 7.0 for objects, and limit y to be within -4.0 and 4.0 for objects.
Place the objects near the center of the frame, without overlapping with each other."""

_prompt_animation_rag_query_generation = """You are an expert in Manim (Community Edition) and its plugins. Your task is to transform a topic for a Manim animation scene into queries that can be used to retrieve relevant documentation from both Manim core and any relevant plugins.

Your queries should include keywords related to the specific Manim classes, methods, functions, and *concepts* that are likely to be used to implement the scene, including any plugin-specific functionality. Focus on extracting the core concepts, actions, and vocabulary from the *entire* scene plan. Generate queries that are concise and target different aspects of the documentation (class reference, method usage, animation examples, conceptual explanations) across both Manim core and relevant plugins.

Here is the Topic (and the context):

{topic}. {context}

Based on the topic and the context, generate multiple human-like queries (maximum 5-7) for retrieving relevant documentation. Please ensure that the search targets are different so that the RAG can retrieve a diverse set of documents covering various aspects of the implementation.

**Specifically, ensure that:**
1. At least 1-2 queries are focused on retrieving information about Manim *function usage* in Manim scenes
2. If the topic and the context can be linked to the use of plugin functionality, include at least 1 query specifically targeting plugin documentation
3. Queries should be specific enough to distinguish between core Manim and plugin functionality when relevant

The above text explanations are relevant to these plugins: {relevant_plugins}

Output the queries in the following format:
```json
[
    {{"query": "content of query 1", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 2", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 3", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 4", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 5", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 6", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 7", "type": "manim_core/name_of_the_plugin"}},
]
```"""

_code_font_size = """If there is title text, font size is highly recommended to be 28.
If there are side labels, font size is highly recommended to be 24.
If there are formulas, font size is highly recommended to be 24.

However, if the text has more than 10 words, font size should be reduced further and mutiple lines should be used."""

_prompt_best_practices = """# Best practices for generating educational videos with manim

1. Specify positions as relative to other objects whenever it makes sense.
   * For example, if you want to place a label for a geometric object.
2. Objects should be of different color from the black background.
3. Keep the text on screen concise.
   * On-screen elements should focus on showcasing the concept, examples and visuals. Labels and illustrative text are still encouraged.
   * For explanations and observations, prefer narrations over on-screen text.
   * You should still show calculations and algorithms in full on screen.
   * For examples and practice problems, it is reasonable to show more text, especially key statements.
   * Longer text should appear smaller to fit on screen.
4. To control the timing of objects appearing:
   * `add` has instantaneous effect, best used for the initial setup of the scene.
   * Animations are best used during narration.
   * Make sure the animations make sense. If an object is already on screen, it makes no sense to fade it in or create it again.
5. Use TeX or MathTeX whenever you want to display math, including symbols and formulas.
"""

_prompt_scene_plan = """You are an expert in educational video production, instructional design, and {topic}. Please design a high-quality video to provide in-depth explanation on {topic}.

**Video Overview:**

Topic: {topic}
Description: {description}

**Scene Breakdown:**

Plan individual scenes. For each scene please provide the following:

*   **Scene Title:** Short, descriptive title (2-5 words).
*   **Scene Purpose:** Learning objective of this scene. How does it connect to previous scenes?
*   **Scene Description:** Detailed description of scene content.
*   **Scene Layout:** Detailedly describe the spatial layout concept. Consider safe area margins and minimum spacing between objects.

Please generate the scene plan for the video in the following format:

```xml
<SCENE_OUTLINE>
    <SCENE_1>
    Scene Title: [Title]
    Scene Purpose: [Learning objective, connection to previous scene]
    Scene Description: [Brief content description]
    Scene Layout: [Spatial layout concept, consider safe area and spacing]
    </SCENE_1>

    <SCENE_2>
    ...
    </SCENE_2>
...
</SCENE_OUTLINE>
```

**Spatial Constraints:**
*   **Safe area margins:** 0.5 units on all sides from the scene edges. *All objects must be positioned within these margins.*
*   **Minimum spacing:** 0.3 units between any two Manim objects (measured edge to edge). *Ensure adequate spacing to prevent overlaps and maintain visual clarity.*

Requirements:
1. Scenes must build progressively, starting from foundational concepts and advancing to more complex ideas to ensure a logical flow of understanding for the viewer. Each scene should naturally follow from the previous one, creating a cohesive learning narrative. Start with simpler scene layouts and progressively increase complexity in later scenes.
2. The total number of scenes should be between 2 and 4.
3. Learning objectives should be distributed evenly across the scenes.
4. The total video duration must be under 15 minutes.
5. It is essential to use the exact output format, tags, and headers as specified in the prompt.
6. Maintain consistent formatting throughout the entire scene plan.
7. **No External Assets:** Do not import any external files (images, audio, video). *Use only Manim built-in elements and procedural generation.
8. **Focus on in-depth explanation of the theorem. Do not include any promotional elements (like YouTube channel promotion, subscribe messages, or external resources) or quiz sessions. Detailed example questions are acceptable and encouraged.**

Note: High-level plan. Detailed scene specifications will be generated later, ensuring adherence to safe area margins and minimum spacing. The spatial constraints defined above will be strictly enforced in subsequent planning stages."""

_prompt_rag_query_generation_technical = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to analyze a storyboard plan and generate effective queries that will retrieve relevant technical documentation about implementation details.

Here is the storyboard plan:

{storyboard}

Based on this storyboard plan, generate multiple human-like queries (maximum 10) for retrieving relevant technical documentation.

**Specifically, ensure that:**
1. Queries focus on retrieving information about **core Manim functionality** and implementation details
2. Include queries about **complex animations and effects** described in the storyboard
3. If the storyboard suggests using plugin functionality, include specific queries targeting those plugin's technical documentation

The above storyboard plan is relevant to these plugins: {relevant_plugins}
Note that you MUST NOT use the plugins that are not listed above.

You MUST only output the queries in the following JSON format (with json triple backticks):
```json
[
    {{"type": "manim-core", "query": "content of core functionality query"}},
    {{"type": "<plugin-name>", "query": "content of plugin-specific query"}},
    {{"type": "manim-core", "query": "content of animation technique query"}}
    ...
]
``` """

_prompt_rag_query_generation_fix_error = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to transform a Manim error and its associated code into effective queries that will retrieve relevant information from Manim documentation.

Here is the error message:
{error}

Here is the Manim code that caused the error:
{code}

Based on the error and code, generate multiple human-like queries (maximum 10) for retrieving relevant documentation. Please ensure that the search targets are different so that the RAG can retrieve a diverse set of documents covering various aspects of the implementation.

**Specifically, ensure that:**
1.  At least some queries are focused on retrieving information about **Manim function usage** in scenes. Frame these queries to target function definitions, usage examples, and parameter details within Manim documentation.
2.  If the error suggests using plugin functionality, include at least 1 query specifically targeting **plugin documentation**.  Clearly mention the plugin name in these queries to focus the search.
3.  Queries should be specific enough to distinguish between core Manim and plugin functionality when relevant, and to target the most helpful sections of the documentation (API reference, tutorials, examples).

The above error and code are relevant to these plugins: {relevant_plugins}.
Note that you MUST NOT use the plugins that are not listed above.

You MUST only output the queries in the following JSON format (with json triple backticks):
```json
[
    {{"type": "manim-core", "query": "content of function usage query"}},
    {{"type": "<plugin-name>", "query": "content of plugin-specific query"}},
    {{"type": "manim-core", "query": "content of API reference query"}}
    ...
]
``` """

_code_disable = """"""

_prompt_manim_cheatsheet = """The followings are the inheritance diagram of the Manim library. You can take as reference to select which class to use for the animation.

``` 
digraph Animation {
    "AddTextLetterByLetter"
    "ShowIncreasingSubsets"
    "ShowIncreasingSubsets" -> "AddTextLetterByLetter"
    "AddTextWordByWord";
    "Succession";
    "Succession" -> "AddTextWordByWord";
    "AnimatedBoundary";
    "VGroup";
    "VGroup" -> "AnimatedBoundary";
    "Animation";
    "AnimationGroup";
    "Animation" -> "AnimationGroup";
    "ApplyComplexFunction";
    "ApplyMethod";
    "ApplyMethod" -> "ApplyComplexFunction";
    "ApplyFunction";
    "Transform";
    "Transform" -> "ApplyFunction";
    "ApplyMatrix";
    "ApplyPointwiseFunction";
    "ApplyPointwiseFunction" -> "ApplyMatrix";
    "ApplyMethod";
    "Transform" -> "ApplyMethod";
    "ApplyPointwiseFunction";
    "ApplyMethod" -> "ApplyPointwiseFunction";
    "ApplyPointwiseFunctionToCenter";
    "ApplyPointwiseFunction" -> "ApplyPointwiseFunctionToCenter";
    "ApplyWave";
    "Homotopy";
    "Homotopy" -> "ApplyWave";
    "Broadcast";
    "LaggedStart";
    "LaggedStart" -> "Broadcast";
    "ChangeDecimalToValue";
    "ChangingDecimal";
    "ChangingDecimal" -> "ChangeDecimalToValue";
    "ChangeSpeed";
    "Animation" -> "ChangeSpeed";
    "ChangingDecimal";
    "Animation" -> "ChangingDecimal";
    "Circumscribe";
    "Succession" -> "Circumscribe";
    "ClockwiseTransform";
    "Transform" -> "ClockwiseTransform";
    "ComplexHomotopy";
    "Homotopy" -> "ComplexHomotopy";
    "CounterclockwiseTransform";
    "Transform" -> "CounterclockwiseTransform";
    "Create";
    "ShowPartial";
    "ShowPartial" -> "Create";
    "CyclicReplace";
    "Transform" -> "CyclicReplace";
    "DrawBorderThenFill";
    "Animation" -> "DrawBorderThenFill";
    "FadeIn";
    "FadeOut";
    "FadeToColor";
    "ApplyMethod" -> "FadeToColor";
    "FadeTransform";
    "Transform" -> "FadeTransform";
    "FadeTransformPieces";
    "FadeTransform" -> "FadeTransformPieces";
    "Flash";
    "AnimationGroup" -> "Flash";
    "FocusOn";
    "Transform" -> "FocusOn";
    "GrowArrow";
    "GrowFromPoint";
    "GrowFromPoint" -> "GrowArrow";
    "GrowFromCenter";
    "GrowFromPoint" -> "GrowFromCenter";
    "GrowFromEdge";
    "GrowFromPoint" -> "GrowFromEdge";
    "GrowFromPoint";
    "Transform" -> "GrowFromPoint";
    "Homotopy";
    "Animation" -> "Homotopy";
    "Indicate";
    "Transform" -> "Indicate";
    "LaggedStart";
    "AnimationGroup" -> "LaggedStart";
    "LaggedStartMap";
    "LaggedStart" -> "LaggedStartMap";
    "MaintainPositionRelativeTo";
    "Animation" -> "MaintainPositionRelativeTo";
    "Mobject";
    "MoveAlongPath";
    "Animation" -> "MoveAlongPath";
    "MoveToTarget";
    "Transform" -> "MoveToTarget";
    "PhaseFlow";
    "Animation" -> "PhaseFlow";
    "RemoveTextLetterByLetter";
    "AddTextLetterByLetter" -> "RemoveTextLetterByLetter";
    "ReplacementTransform";
    "Transform" -> "ReplacementTransform";
    "Restore";
    "ApplyMethod" -> "Restore";
    "Rotate";
    "Transform" -> "Rotate";
    "Rotating";
    "Animation" ->  "Rotating";
    "ScaleInPlace";
    "ApplyMethod" -> "ScaleInPlace";
    "ShowIncreasingSubsets";
    "Animation" -> "ShowIncreasingSubsets";
    "ShowPartial";
    "Animation" -> "ShowPartial";
    "ShowPassingFlash";
    "ShowPartial" -> "ShowPassingFlash";
    "ShowPassingFlashWithThinningStrokeWidth";
    "AnimationGroup" ->  "ShowPassingFlashWithThinningStrokeWidth";
    "ShowSubmobjectsOneByOne";
    "ShowIncreasingSubsets" -> "ShowSubmobjectsOneByOne";
    "ShrinkToCenter";
    "ScaleInPlace" -> "ShrinkToCenter";
    "SmoothedVectorizedHomotopy";
    "Homotopy" -> "SmoothedVectorizedHomotopy";
    "SpinInFromNothing";
    "GrowFromCenter" -> "SpinInFromNothing";
    "SpiralIn";
    "Animation" -> "SpiralIn";
    "Succession";
    "AnimationGroup" -> "Succession";
    "Swap";
    "CyclicReplace" -> "Swap";
    "TracedPath";
    "VMobject";
    "VMobject" -> "TracedPath";
    "Transform";
    "Animation" -> "Transform";
    "TransformAnimations";
    "Transform" -> "TransformAnimations";
    "TransformFromCopy";
    "Transform" -> "TransformFromCopy";
    "TransformMatchingAbstractBase";
    "AnimationGroup" -> "TransformMatchingAbstractBase";
    "TransformMatchingShapes";
    "TransformMatchingAbstractBase" -> "TransformMatchingShapes";
    "TransformMatchingTex";
    "TransformMatchingAbstractBase" ->  "TransformMatchingTex";
    "Uncreate";
    "Create" -> "Uncreate";
    "Unwrite";
    "Write";
    "Write" -> "Unwrite";
    "UpdateFromAlphaFunc";
    "UpdateFromFunc";
    "UpdateFromFunc" -> "UpdateFromAlphaFunc";
    "UpdateFromFunc";
    "Animation" -> "UpdateFromFunc";
    "VGroup";
    "VMobject" ->  "VGroup";
    "VMobject";
    "Mobject" -> "VMobject";

    "Wait";
    "Animation" -> "Wait";
    "Wiggle";
    "Animation" -> "Wiggle";
    "Write";
    "DrawBorderThenFill" ->  "Write";
}
```


```
digraph Camera {
    "BackgroundColoredVMobjectDisplayer"
    "Camera"
    "MappingCamera"
    "Camera" -> "MappingCamera"
    "MovingCamera"
    "Camera" -> "MovingCamera"
    "MultiCamera"
    "MovingCamera" -> "MultiCamera"
    "OldMultiCamera"
    "Camera" -> "OldMultiCamera"
    "SplitScreenCamera"
    "OldMultiCamera" -> "SplitScreenCamera"
    "ThreeDCamera"
    "Camera" -> "ThreeDCamera"
}
```

```
digraph MObject {
    "AbstractImageMobject"
    "Mobject" -> "AbstractImageMobject"
    "Angle"
    "VMobject" -> "Angle"
    "AnnotationDot"
    "Dot" -> "AnnotationDot"
    "AnnularSector"
    "Arc" -> "AnnularSector"
    "Annulus"
    "Circle" -> "Annulus"
    "Arc"
    "TipableVMobject" -> "Arc"
    "ArcBetweenPoints"
    "Arc" -> "ArcBetweenPoints"
    "ArcBrace"
    "Brace" -> "ArcBrace"
    "ArcPolygon"
    "VMobject" -> "ArcPolygon"
    "ArcPolygonFromArcs"
    "VMobject" -> "ArcPolygonFromArcs"
    "Arrow"
    "Line" -> "Arrow"
    "Arrow3D"
    "Line3D" -> "Arrow3D"
    "ArrowCircleFilledTip"
    "ArrowCircleTip" -> "ArrowCircleFilledTip"
    "ArrowCircleTip"
    "ArrowTip" -> "ArrowCircleTip"
    "Circle" -> "ArrowCircleTip"
    "ArrowSquareFilledTip"
    "ArrowSquareTip" -> "ArrowSquareFilledTip"
    "ArrowSquareTip"
    "ArrowTip" -> "ArrowSquareTip"
    "Square" -> "ArrowSquareTip"
    "ArrowTip"
    "VMobject" -> "ArrowTip"
    "ArrowTriangleFilledTip"
    "ArrowTriangleTip" -> "ArrowTriangleFilledTip"
    "ArrowTriangleTip"
    "ArrowTip" -> "ArrowTriangleTip"
    "Triangle" -> "ArrowTriangleTip"
    "ArrowVectorField"
    "VectorField" -> "ArrowVectorField"
    "Axes"
    "VGroup" -> "Axes"
    "CoordinateSystem" -> "Axes"
    "BackgroundRectangle"
    "SurroundingRectangle" -> "BackgroundRectangle"
    "BarChart"
    "Axes" -> "BarChart"
    "Brace"
    "svg_mobject.VMobjectFromSVGPath" -> "Brace"
    "BraceBetweenPoints"
    "Brace" -> "BraceBetweenPoints"
    "BraceLabel"
    "VMobject" -> "BraceLabel"
    "BraceText"
    "BraceLabel" -> "BraceText"
    "BulletedList"
    "Tex" -> "BulletedList"
    "Circle"
    "Arc" -> "Circle"
    "Code"
    "VGroup" -> "Code"
    "ComplexPlane"
    "NumberPlane" -> "ComplexPlane"
    "ComplexValueTracker"
    "ValueTracker" -> "ComplexValueTracker"
    "Cone"
    "Surface" -> "Cone"
    "CoordinateSystem"
    "Cross"
    "VGroup" -> "Cross"
    "Cube"
    "VGroup" -> "Cube"
    "CubicBezier"
    "VMobject" -> "CubicBezier"
    "CurvedArrow"
    "ArcBetweenPoints" -> "CurvedArrow"
    "CurvedDoubleArrow"
    "CurvedArrow" -> "CurvedDoubleArrow"
    "CurvesAsSubmobjects"
    "VGroup" -> "CurvesAsSubmobjects"
    "Cutout"
    "VMobject" -> "Cutout"
    "Cylinder"
    "Surface" -> "Cylinder"
    "DashedLine"
    "Line" -> "DashedLine"
    "DashedVMobject"
    "VMobject" -> "DashedVMobject"
    "DecimalMatrix"
    "Matrix" -> "DecimalMatrix"
    "DecimalNumber"
    "VMobject" -> "DecimalNumber"
    "DecimalTable"
    "Table" -> "DecimalTable"
    "DiGraph"
    "GenericGraph" -> "DiGraph"
    "Difference"
    "Dodecahedron"
    "Polyhedron" -> "Dodecahedron"
    "Dot"
    "Circle" -> "Dot"
    "Dot3D"
    "Sphere" -> "Dot3D"
    "DoubleArrow"
    "Arrow" -> "DoubleArrow"
    "Elbow"
    "VMobject" -> "Elbow"
    "Ellipse"
    "Circle" -> "Ellipse"
    "Exclusion"
    "FullScreenRectangle"
    "ScreenRectangle" -> "FullScreenRectangle"
    "FunctionGraph"
    "ParametricFunction" -> "FunctionGraph"
    "Generic"
    "GenericGraph"
    "Generic" -> "GenericGraph"
    "Graph"
    "GenericGraph" -> "Graph"
    "Group"
    "Mobject" -> "Group"
    "Icosahedron"
    "Polyhedron" -> "Icosahedron"
    "ImageMobject"
    "AbstractImageMobject" -> "ImageMobject"
    "ImageMobjectFromCamera"
    "AbstractImageMobject" -> "ImageMobjectFromCamera"
    "ImplicitFunction"
    "VMobject" -> "ImplicitFunction"
    "Integer"
    "DecimalNumber" -> "Integer"
    "IntegerMatrix"
    "Matrix" -> "IntegerMatrix"
    "IntegerTable"
    "Table" -> "IntegerTable"
    "Intersection"
    "LabeledDot"
    "Dot" -> "LabeledDot"
    "LayoutFunction"
    "Protocol" -> "LayoutFunction"
    "Line"
    "TipableVMobject" -> "Line"
    "Line3D"
    "Cylinder" -> "Line3D"
    "LinearBase"
    "LogBase"
    "ManimBanner"
    "VGroup" -> "ManimBanner"
    "MarkupText"
    "svg_mobject.SVGMobject" -> "MarkupText"
    "MathTable"
    "Table" -> "MathTable"
    "MathTex"
    "SingleStringMathTex" -> "MathTex"
    "Matrix"
    "VMobject" -> "Matrix"
    "Mobject"
    "Mobject1D"
    "PMobject" -> "Mobject1D"
    "Mobject2D"
    "PMobject" -> "Mobject2D"
    "MobjectMatrix"
    "Matrix" -> "MobjectMatrix"
    "MobjectTable"
    "Table" -> "MobjectTable"
    "NumberLine"
    "Line" -> "NumberLine"
    "NumberPlane"
    "Axes" -> "NumberPlane"
    "Octahedron"
    "Polyhedron" -> "Octahedron"
    "PGroup"
    "PMobject" -> "PGroup"
    "PMobject"
    "Mobject" -> "PMobject"
    "Paragraph"
    "VGroup" -> "Paragraph"
    "ParametricFunction"
    "VMobject" -> "ParametricFunction"
    "Point"
    "PMobject" -> "Point"
    "PointCloudDot"
    "Mobject1D" -> "PointCloudDot"
    "PolarPlane"
    "Axes" -> "PolarPlane"
    "Polygon"
    "Polygram" -> "Polygon"
    "Polygram"
    "VMobject" -> "Polygram"
    "Polyhedron"
    "VGroup" -> "Polyhedron"
    "Prism"
    "Cube" -> "Prism"
    "Protocol"
    "Generic" -> "Protocol"
    "Rectangle"
    "Polygon" -> "Rectangle"
    "RegularPolygon"
    "RegularPolygram" -> "RegularPolygon"
    "RegularPolygram"
    "Polygram" -> "RegularPolygram"
    "RightAngle"
    "Angle" -> "RightAngle"
    "RoundedRectangle"
    "Rectangle" -> "RoundedRectangle"
    "SVGMobject"
    "VMobject" -> "SVGMobject"
    "SampleSpace"
    "Rectangle" -> "SampleSpace"
    "ScreenRectangle"
    "Rectangle" -> "ScreenRectangle"
    "Sector"
    "AnnularSector" -> "Sector"
    "SingleStringMathTex"
    "svg_mobject.SVGMobject" -> "SingleStringMathTex"
    "Sphere"
    "Surface" -> "Sphere"
    "Square"
    "Rectangle" -> "Square"
    "Star"
    "Polygon" -> "Star"
    "StealthTip"
    "ArrowTip" -> "StealthTip"
    "StreamLines"
    "VectorField" -> "StreamLines"
    "Surface"
    "VGroup" -> "Surface"
    "SurroundingRectangle"
    "RoundedRectangle" -> "SurroundingRectangle"
    "Table"
    "VGroup" -> "Table"
    "TangentLine"
    "Line" -> "TangentLine"
    "Tetrahedron"
    "Polyhedron" -> "Tetrahedron"
    "Tex"
    "MathTex" -> "Tex"
    "Text"
    "svg_mobject.SVGMobject" -> "Text"
    "ThreeDAxes"
    "Axes" -> "ThreeDAxes"
    "ThreeDVMobject"
    "VMobject" -> "ThreeDVMobject"
    "TipableVMobject"
    "VMobject" -> "TipableVMobject"
    "Title"
    "Tex" -> "Title"
    "Torus"
    "Surface" -> "Torus"
    "Triangle"
    "RegularPolygon" -> "Triangle"
    "Underline"
    "Line" -> "Underline"
    "Union"
    "UnitInterval"
    "NumberLine" -> "UnitInterval"
    "VDict"
    "VMobject" -> "VDict"
    "VGroup"
    "VMobject" -> "VGroup"
    "VMobject"
    "Mobject" -> "VMobject"
    "VMobjectFromSVGPath"
    "VMobject" -> "VMobjectFromSVGPath"
    "ValueTracker"
    "Mobject" -> "ValueTracker"
    "Variable"
    "VMobject" -> "Variable"
    "Vector"
    "Arrow" -> "Vector"
    "VectorField"
    "VGroup" -> "VectorField"
    "VectorizedPoint"
    "VMobject" -> "VectorizedPoint"
}
```

```
digraph Scene {
    "LinearTransformationScene"
    "VectorScene"
    "VectorScene" -> "LinearTransformationScene"
    "MovingCameraScene"
    "Scene"
    "Scene" -> "MovingCameraScene"
    "RerunSceneHandler"
    "Scene"
    "SceneFileWriter"
    "SpecialThreeDScene"
    "ThreeDScene"
    "ThreeDScene" -> "SpecialThreeDScene"
    "ThreeDScene"
    "Scene" -> "ThreeDScene"
    "VectorScene"
    "Scene" -> "VectorScene"
    "ZoomedScene"
    "MovingCameraScene" -> "ZoomedScene"
}
```"""

_prompt_rag_query_generation_vision_storyboard = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to analyze a scene plan for a Manim animation and generate effective queries that will retrieve relevant documentation about visual elements and scene composition.

Here is the scene plan:

{scene_plan}

Based on this scene plan, generate multiple human-like queries (maximum 10) for retrieving relevant documentation about visual elements and scene composition techniques.

**Specifically, ensure that:**
1. Queries focus on retrieving information about **visual elements** like shapes, objects, and their properties
2. Include queries about **scene composition techniques** like layout, positioning, and grouping
3. If the scene plan suggests using plugin functionality, include specific queries targeting those plugin's visual capabilities
4. Queries should be high-level, aiming to discover what Manim features can be used, rather than focusing on low-level implementation details.
    - For example, instead of "how to set the color of a circle", ask "what visual properties of shapes can I control in Manim?".

The above scene plan is relevant to these plugins: {relevant_plugins}.
Note that you MUST NOT use the plugins that are not listed above.

You MUST only output the queries in the following JSON format (with json triple backticks):
```json
[
    {{"type": "manim-core", "query": "content of visual element query"}},
    {{"type": "<plugin-name>", "query": "content of plugin-specific query"}},
    {{"type": "manim-core", "query": "content of composition technique query"}}
    ...
]
```"""

_prompt_context_learning_technical_implementation = """Here are some example technical implementation plans to help guide your implementation:

{examples}

Please follow a similar structure while maintaining creativity and relevance to the current scene."""

_prompt_detect_plugins = """You are a Manim plugin detection system. Your task is to analyze a video topic and description to determine which Manim plugins would be most relevant for the actual animation implementation needs.

Topic:
{topic}

Description:
{description}

Available Plugins:
{plugin_descriptions}

Instructions:
1. Analyze the topic and description, focusing specifically on what needs to be animated
2. Review each plugin's capabilities and determine if they provide specific tools needed for the animations described
3. Only select plugins that provide functionality directly needed for the core animations
4. Consider these criteria for each plugin:
   - Does the plugin provide specific tools or components needed for the main visual elements?
   - Are the plugin's features necessary for implementing the core animations?
   - Would the animation be significantly more difficult to create without this plugin?
5. Exclude plugins that:
   - Only relate to the general topic area but don't provide needed animation tools
   - Might be "nice to have" but aren't essential for the core visualization
   - Could be replaced easily with basic Manim shapes and animations

Your response must follow the output format below:
<THINKING>
[brief description of your thinking process]
</THINKING>
<PLUGINS>
```json
["plugin_name1", "plugin_name2"]
```
</PLUGINS>"""

_prompt_scene_animation_narration = """You are an expert in educational video production and Manim animation, skilled in creating engaging and pedagogically effective learning experiences.  
**Reminder:** This animation and narration plan is entirely self-contained; there is no dependency on any previous or subsequent scene implementations. However, the narration should flow smoothly as part of a larger, single video.

Your task is to create a **detailed animation and narration plan for Scene {scene_number}**, ensuring it is not just visually appealing but also serves a clear educational purpose within the overall video topic.

Remember, the narration should not simply describe what's happening visually, but rather **teach a concept step-by-step**, guiding the viewer to a deeper understanding.  Animations should be spatially coherent, contribute to a clear visual flow, and strictly respect safe area margins (0.5 units) and minimum spacing (0.3 units).  **Consider the scene number {scene_number} and the overall scene context to ensure smooth transitions and a logical flow within the larger video narrative.**

Topic: {topic}
Description: {description}

Scene Overview:
{scene_outline}

Scene Vision and Storyboard:
{scene_vision_storyboard}

Technical Implementation Plan:
{technical_implementation_plan}

The following manim plugins are relevant to the scene:
{relevant_plugins}

**Spatial Constraints (Strictly Enforced Throughout Animations):**
*   **Safe area margins:** 0.5 units. *Maintain objects and VGroups within margins.*
*   **Minimum spacing:** 0.3 units. *Ensure minimum spacing between all objects and VGroups.*

**Animation Timing and Pacing Requirements:**
*   Specify `run_time` for all animations.
*   Use `Wait()` for transition buffers, specifying durations and **pedagogical purpose**.
*   Coordinate animation timings with narration cues for synchronized pedagogical presentation.

**Visual Flow and Pedagogical Clarity:**
*   Ensure animations create a clear and logical visual flow, **optimized for learning and concept understanding.**
*   Use animation pacing and transition buffers to visually separate ideas and **enhance pedagogical clarity.**
*   Maintain spatial coherence for predictable and understandable animations, strictly adhering to spatial constraints.

**Diagrams/Sketches (Optional but Highly Recommended for Complex Scenes):**
*   For complex animations, include diagrams/sketches to visualize animation flow and object movements. This aids clarity and reduces errors.

Your plan must demonstrate a strong understanding of pedagogical narration and how animations can be used to effectively teach concepts, while strictly adhering to spatial constraints and timing requirements.

You MUST generate a **detailed and comprehensive** animation and narration plan for **Scene {scene_number}**, in the following format, similar to the example provided (from ```xml to </SCENE_ANIMATION_NARRATION_PLAN>```):

```xml
<SCENE_ANIMATION_NARRATION_PLAN>

[ANIMATION_STRATEGY]
1. **Pedagogical Animation Plan:** Provide a detailed plan for all animations in the scene, explicitly focusing on how each animation contributes to **teaching the core concepts** of this scene.
    - **Parent VGroup transitions (if applicable):**
        - If VGroups are used, specify transitions (`Shift`, `Transform`, `FadeIn`, `FadeOut`) with `Animation` type, direction, magnitude, target VGroup, and `run_time`.
        - **Explain the pedagogical rationale** for each VGroup transition. How does it guide the viewer's attention or contribute to understanding the scene's learning objectives? Ensure spatial coherence and respect for constraints.
    - **Element animations within VGroups and for individual Mobjects:**
        - Specify animation types (`Create`, `Write`, `FadeIn`, `Transform`, `Circumscribe`, `AnimationGroup`, `Succession`) for elements.
        - For each element animation, specify `Animation` type, target object(s), and `run_time`. Detail sequences and timing for `AnimationGroup` or `Succession`.
        - **Explain the pedagogical purpose** of each element animation. How does it break down complex information, highlight key details, or improve visual clarity for learning? Ensure spatial coherence and minimum spacing.
        - **Coordinate element animations with VGroup transitions:**
            - Clearly describe the synchronization between element animations and VGroup transitions (if any).
            - Specify relative timing and `run_time` to illustrate coordination.
            - **Explain how this animation sequence and coordination creates a pedagogical flow**, guiding the viewer's eye and attention logically through the learning material.

2. **Scene Flow - Pedagogical Pacing and Clarity:** Detail the overall flow of the scene, emphasizing pedagogical effectiveness.
    - **Overall animation sequence, spatial progression for learning:**
        - Describe the complete animation sequence, broken down into pedagogical sub-sections (e.g., "Introducing the Problem", "Step-by-step Solution", "Concept Reinforcement").
        - Outline the spatial progression of objects and VGroups, focusing on how it supports the **pedagogical narrative** and concept development.
        - Ensure a clear and logical visual flow optimized for learning, respecting spatial constraints.
    - **Transition buffers for pedagogical pauses:**
        - Specify `Wait()` times between animation sections for visual separation and **learner processing time**.
        - For each `Wait()`, specify duration and **explain the pedagogical reason** for this buffer (e.g., "Allow viewers time to process the formula", "Create a pause for reflection before moving to the next concept").
    - **Coordinate animation timing with narration for engagement and comprehension:**
        - Describe how animation timings are coordinated with the narration script to **maximize viewer engagement and comprehension**.
        - Specify animation cues within the narration script and explain how these cues are synchronized with animations to **reinforce learning points** at the optimal moment.

[NARRATION]
- **Pedagogical Narration Script:**
    - Provide the full narration script for Scene {scene_number}.
    - **Embed precise animation timing cues** within the narration script (as described before).
    - **The script should be written as if delivered by a knowledgeable and engaging lecturer.** It should:
        - **Clearly explain concepts step-by-step.**
        - **Use analogies and real-world examples to enhance understanding.**
        - **Pose questions to encourage active thinking.**
        - **Summarize key points and transitions.**
        - **Be detailed and knowledge-rich, not just visually descriptive.**
        - **Connect smoothly with the previous and subsequent scenes, acting as a segment within a single, cohesive video. 
        - Avoid repetitive introductions or conclusions.** 
        - Consider using phrases like "Building on what we saw in the previous part..." or "Let's now move on to..." to create a sense of continuity.
        - Reference the scene number when appropriate (e.g., "Now, let's explore...").
    - **Crucially, the narration should seamlessly integrate with the animations to create a cohesive and effective learning experience.**
- **Narration Sync - Pedagogical Alignment:**
    - Detail the synchronization strategy between narration and animations, emphasizing **pedagogical alignment**.
    - Explain how narration timing is aligned with animation start/end times to **guide viewer attention to key learning elements precisely when they animate.**
    - Emphasize how narration cues and animation timings work together to **create a synchronized audiovisual presentation that maximizes learning and retention.**

</SCENE_ANIMATION_NARRATION_PLAN>
```
"""

_code_color_cheatsheet = """MUST include the following color definitions if you use the colors in your code. ONLY USE THE COLORS BELOW.

WHITE = '#FFFFFF'
RED = '#FF0000'
GREEN = '#00FF00'
BLUE = '#0000FF'
YELLOW = '#FFFF00'
CYAN = '#00FFFF'
MAGENTA = '#FF00FF'
ORANGE = '#FFA500'
PURPLE = '#800080'
PINK = '#FFC0CB'
BROWN = '#A52A2A'
GRAY = '#808080'
TEAL = '#008080'
NAVY = '#000080'
OLIVE = '#808000'
MAROON = '#800000'
LIME = '#00FF00'
AQUA = '#00FFFF'
FUCHSIA = '#FF00FF'
SILVER = '#C0C0C0'
GOLD = '#FFD700'"""

_prompt_visual_self_reflection = """You are an expert in Manim animations and educational video quality assessment. Your task is to analyze a rendered Manim video and its corresponding audio narration to identify areas for visual and auditory improvement, ensuring alignment with the provided implementation plan and enhancing the video's teaching effectiveness.

Please analyze the provided Manim video and listen to the accompanying audio narration. Conduct a thorough self-reflection focusing on the following aspects:

**1. Visual Presentation and Clarity (Automated VLM Analysis & Expert Human-like Judgment):**

*   **Object Overlap:** Does the video exhibit any visual elements (text, shapes, equations, etc.) overlapping in a way that obscures information or makes the animation difficult to understand? If possible, Detect regions of significant overlap and highlight them in your reflection.
*   **Out-of-Bounds Objects:** Are any objects positioned partially or entirely outside of the visible frame of the video? Identify and report objects that appear to be clipped or outside the frame boundaries.
*   **Incorrect Object Positioning:** Based on your understanding of good visual design and the scene's educational purpose, are objects placed in positions that are illogical, distracting, or misaligned with their intended locations or relationships to other elements as described in the implementation plan? Consider:
    *   **Logical Flow:** Does the spatial arrangement support the intended visual flow and narrative progression of the scene?
    *   **Alignment and Balance:** Is the scene visually balanced? Are elements aligned in a way that is aesthetically pleasing and contributes to clarity, or does the layout appear haphazard or unbalanced?
    *   **Proximity and Grouping:** Are related elements positioned close enough to be visually grouped, and are unrelated elements sufficiently separated to avoid visual clutter?
*   **General Visual Clarity & Effectiveness:** Consider broader aspects of visual communication. Are there any other issues that detract from the video's clarity, impact, or overall effectiveness? This could include:
    *   **Visual Clutter:** Is the scene too busy or visually overwhelming at any point? Are there too many elements on screen simultaneously?
    *   **Poor Spacing/Layout:** Is the spacing between elements inconsistent or inefficient, making the scene feel cramped or unbalanced? Are margins and padding used effectively?
    *   **Ineffective Use of Color:** Are color choices distracting, clashing, or not contributing to the animation's message? Are colors used consistently and purposefully to highlight key information?
    *   **Pacing Issues (Visual):** Is the visual animation too fast or too slow in certain sections, hindering comprehension? Are visual transitions smooth and well-timed?
    *   **Animation Clarity:** Are the animations themselves clear and helpful in conveying the intended information? Do animations effectively guide the viewer's eye and focus attention?

**2. Narration Quality:**

*   **Narration Clarity and Pacing:** Is the narration clear, concise, and easy to understand? Is the pacing of the narration appropriate for the visual content and the target audience? Does the narration effectively support the visual explanations?
*   **Narration Sync with Visuals:** Does the narration effectively synchronize with the on-screen visuals? Use VLM to analyze the video and identify instances where the narration is misaligned with the animations or visual elements it is describing. Report specific timings of misalignment.

**3. Alignment with Implementation Plan:**

*   **Visual Fidelity:** Does the rendered video accurately reflect the visual elements and spatial arrangements described in the provided Manim Implementation Plan? Identify any deviations.
*   **Animation Fidelity:** Do the animations in the video match the animation methods and sequences outlined in the Implementation Plan? Report any discrepancies.

Manim Implementation Plan:
{implementation}

Generated Code:
{generated_code}

Output Format 1:
If any issues are identified in visual presentation, audio quality, narration, or plan alignment, please provide a detailed reflection on the issues and how to improve the video's visual and auditory quality, narration effectiveness, and code correctness. Then, you must return the updated Python code that directly addresses these issues. The code must be complete and executable.

<reflection>
[Detailed reflection on visual, auditory, narration, and plan alignment issues and improvement suggestions. Include specific timings for narration/visual sync issues and descriptions of object overlap/out-of-bounds problems if detected by VLM.  Be specific about code changes needed for improvement.]
</reflection>
<code>
[Improved Python Code - Complete and Executable - Directly Addressing Reflection Points]
</code>

Output Format 2:
If no issues are found and the video and audio are deemed high quality, visually clear, narratively effective, and fully aligned with the implementation plan, please explicitly only return "<LGTM>" as output."""

_prompt_teaching_framework = """# Comprehensive Educational Video Content Framework

## 1. Pre-Production Planning

### A. Learning Objectives
- **Knowledge Level (Remember & Understand)**
  Define specific, measurable learning outcomes that can be clearly assessed and evaluated. These outcomes should be concrete and observable, allowing instructors to verify that learning has occurred. Each outcome should be written using precise language that leaves no ambiguity about what constitutes success. For example, \"After watching this video, learners will be able to define and explain the concept of variables in programming\" provides a clear benchmark for assessment.

  Action verbs are essential tools for crafting effective learning objectives. Choose verbs like define, list, describe, explain, and identify that clearly indicate the expected cognitive processes. These verbs should align with Bloom's Taxonomy to ensure appropriate cognitive engagement. When applicable, ensure all objectives align with relevant curriculum standards to maintain educational consistency and meet institutional requirements.

- **Comprehension Level (Analyze & Evaluate)**
  Develop objectives that emphasize deeper understanding and connections between concepts. These objectives should go beyond simple recall to require analysis and evaluation of the material. Students should be able to make meaningful connections between different aspects of the content and explain their relationships. For example, \"Learners will be able to compare different data types and explain when to use each\" demonstrates this deeper level of understanding.

  Critical thinking elements should be deliberately incorporated into each objective. Create scenarios that challenge students to apply their knowledge in new contexts. These scenarios should require careful analysis and reasoned decision-making to solve problems effectively. Design learning experiences that encourage students to question assumptions and develop analytical skills.

- **Application Level (Apply & Create)**
  Develop practical skills that directly translate to real-world applications and scenarios. These objectives should focus on hands-on experience and tangible outcomes that demonstrate mastery. For example, \"Learners will be able to write a basic program using variables and proper naming conventions\" provides a clear, actionable goal that can be demonstrated through practical work.

  Include hands-on exercises that allow students to practice and refine their skills in a supported environment. These exercises should gradually increase in complexity to build confidence and competence. Provide real-world context by incorporating authentic scenarios and problems that students might encounter in their future careers or daily lives. This connection to reality helps maintain engagement and demonstrates the immediate value of the learning.

- **Target Audience Analysis**
  Conduct thorough demographic research to understand your learners' backgrounds, ages, and educational levels. This analysis should include assessment of prior knowledge and experience with the subject matter. Consider the technical capabilities of your audience, including their access to necessary tools and technologies.

  Evaluate different learning preferences and styles within your target audience. This understanding helps in designing varied content that appeals to visual, auditory, and kinesthetic learners. Consider cultural and linguistic factors that might impact learning effectiveness. Create content that is inclusive and accessible to learners from diverse backgrounds. Account for varying levels of technical proficiency and ensure your content can be accessed across different devices and platforms.

### B. Content Structure

- **Hook (5-10% of duration)**
  Begin each video with a compelling problem or scenario that immediately captures attention and creates interest. This hook should be relevant to the content while being unexpected or intriguing enough to maintain viewer engagement. Use surprising facts or statistics that challenge common assumptions or demonstrate the importance of the topic.

  Share relevant real-world applications that demonstrate immediate value to the learner. For example, \"What if you could automate your daily tasks with just a few lines of code?\" creates immediate interest by connecting to practical benefits. The hook should create an emotional connection and generate curiosity about the upcoming content. Consider using storytelling elements or real-world problems that your audience can relate to.

- **Context (10-15%)**
  Provide clear explanations of how the content relates to real-world situations and problems. This context should help learners understand why the material is relevant to their lives or career goals. Make explicit connections to previous knowledge and experiences that learners can build upon.

  Address the fundamental question of \"Why should I learn this?\" by demonstrating practical applications and benefits. This explanation should be concrete and specific to your audience's needs and interests. Set clear expectations for learning outcomes so students understand what they will gain from the content. Provide a roadmap for the learning journey ahead, including how this content connects to future topics and skills.

- **Core Content (60-70%)**
  Organize material in a logical progression that builds from fundamental concepts to more complex applications. This progression should be carefully planned to avoid overwhelming learners while maintaining engagement. Include multiple examples that demonstrate concepts from different angles and perspectives.

  Use varied teaching methods to accommodate different learning styles and maintain interest. These methods might include demonstrations, animations, code examples, and interactive elements. Implement frequent knowledge checks throughout the content to ensure understanding and maintain engagement. Break complex topics into manageable chunks that can be easily processed and remembered.

- **Practice/Application (10-15%)**
  Create guided practice opportunities that allow learners to apply new knowledge in a supported environment. These practice sessions should include clear instructions and immediate feedback mechanisms. Design interactive elements that engage learners and require active participation rather than passive viewing.

  Develop problem-solving scenarios that challenge learners to apply concepts in realistic situations. These scenarios should gradually increase in complexity as learners gain confidence. Include opportunities for peer learning and collaboration when possible. Provide scaffolded support that can be gradually removed as learners become more proficient.

- **Summary (5-10%)**
  Conclude each video with a comprehensive recap of key points and main takeaways. This summary should reinforce the most important concepts and their practical applications. Preview upcoming topics to create anticipation and show how current learning connects to future content.

  Provide specific action items that learners can implement immediately to reinforce their learning. These should be concrete, achievable tasks that build confidence and competence. Share additional resources for further learning, including reference materials, practice exercises, and advanced topics. Create clear connections between the current content and future learning objectives.

## 2. Instructional Design Elements

### A. Cognitive Load Management

- **Chunking Strategies**
  Break complex content into manageable segments of 3-5 minutes each. These chunks should focus on single concepts or closely related ideas that form a coherent unit. Use clear transitions between segments to maintain flow while allowing for cognitive processing.

  Implement progressive complexity by building from basic concepts to more advanced applications. This progression should be carefully planned to avoid overwhelming learners. Include strategic pauses and processing time between segments to allow for reflection and integration of new information. Use visual and verbal cues to signal transitions between different concepts or levels of complexity.

- **Visual Organization**
  Develop a consistent visual hierarchy that guides learners through the content effectively. This hierarchy should use size, color, and placement to indicate the relative importance of different elements. Implement clean, uncluttered designs that minimize distractions and focus attention on key concepts.

  Apply color coding consistently to help learners identify and remember related concepts. This coding should be intentional and meaningful, not merely decorative. Use white space effectively to create visual breathing room and help separate different concepts. Ensure that visual elements support rather than compete with the learning objectives.

- **Information Processing**
  Carefully limit the introduction of new concepts to 5-7 per video to prevent cognitive overload. This limitation helps ensure that learners can effectively process and retain the information presented. Develop and use mnemonics and memory aids that help learners organize and remember key concepts.

  Provide visual anchors that learners can reference throughout the content. These anchors should help maintain context and show relationships between concepts. Include strategic review points that reinforce previous learning before introducing new material. Create clear connections between new information and existing knowledge to facilitate better retention.

### B. Engagement Techniques

- **Storytelling Elements**
  Develop a clear narrative flow that carries learners through the content naturally. This narrative should have a beginning, middle, and end that maintains interest and supports learning objectives. Use character-driven examples that learners can relate to and remember.

  Include elements of conflict and resolution to create tension and maintain engagement. These elements should be relevant to the learning objectives and help illustrate key concepts. Maintain an emotional connection through relatable scenarios and authentic problems. Create story arcs that span multiple videos or modules to maintain long-term engagement.

- **Visual Support**
  Create relevant graphics and animations that enhance understanding of key concepts. These visual elements should be purposeful and directly support learning objectives, not merely decorative. Implement a consistent visual style across all content to maintain professionalism and reduce cognitive load.

  Develop clear infographics that break down complex concepts into understandable components. These should use visual hierarchy and design principles effectively. Use motion and animation thoughtfully to direct attention to important elements and demonstrate processes. Ensure all visual elements are accessible and effectively communicate their intended message.

- **Interactive Components**
  Design and embed quiz questions that check understanding at key points in the content. These questions should be strategically placed to maintain engagement and reinforce learning. Include deliberate pause points that encourage reflection and active processing of information.

  Create coding challenges or practical exercises that allow immediate application of concepts. These should be scaffolded appropriately for the learner's skill level. Provide multiple opportunities for feedback, both automated and instructor-guided when possible. Design interactive elements that encourage experimentation and learning from mistakes.

## 3. Content Delivery Framework

### A. Teaching Sequence

1. **Activate**
   Begin each learning session by connecting to familiar concepts that students already understand. This activation of prior knowledge creates a foundation for new learning and helps students feel confident. Use carefully chosen analogies and metaphors that bridge the gap between known and new concepts. These comparisons should be relevant to your audience's experience and background.

   Create explicit connections to previous learning modules or related concepts. These connections help students build a coherent mental model of the subject matter. Assess prior knowledge through quick activities or questions that reveal students' current understanding. Use this assessment to adjust your teaching approach and address any misconceptions early in the lesson.

2. **Present**
   Deliver clear, structured explanations of new concepts that build upon activated knowledge. These explanations should use precise language while remaining accessible to your target audience. Employ multiple representation methods, including verbal explanations, visual diagrams, and interactive demonstrations. This variety helps accommodate different learning styles and reinforces understanding.

   Provide step-by-step demonstrations that break complex processes into manageable parts. Each step should be clearly explained and connected to the overall objective. Include real-world examples that illustrate practical applications of the concepts. These examples should be relevant to your audience's interests and career goals.

3. **Guide**
   Develop worked examples that demonstrate expert problem-solving processes and thinking strategies. These examples should include explicit explanations of decision-making and common pitfalls to avoid. Share expert thinking processes by \"thinking aloud\" through problem-solving steps. This transparency helps students understand the metacognitive aspects of learning.

   Create scaffolded learning experiences that gradually reduce support as students gain confidence. Begin with highly structured guidance and progressively move toward independent work. Address common misconceptions and errors proactively, explaining why they occur and how to avoid them. Provide clear strategies for troubleshooting and problem-solving.

4. **Practice**
   Design guided exercises that allow students to apply new knowledge with appropriate support. These exercises should be carefully sequenced to build confidence and competence gradually. Include opportunities for independent practice that reinforce learning and build autonomy. Ensure these practice sessions are aligned with learning objectives and provide clear success criteria.

   Create peer learning opportunities that allow students to learn from and teach others. These interactions can reinforce understanding and develop communication skills. Implement immediate feedback mechanisms that help students understand their progress and areas for improvement. This feedback should be specific, constructive, and actionable.

5. **Apply**
   Develop real-world projects that require students to integrate and apply their learning in authentic contexts. These projects should be challenging but achievable, with clear connections to practical applications. Create case studies that illustrate complex scenarios and require critical thinking and problem-solving skills. These studies should reflect realistic situations students might encounter in their careers.

   Design problem-solving scenarios that encourage creative application of knowledge and skills. These scenarios should have multiple possible solutions to encourage innovative thinking. Provide opportunities for creative applications that allow students to extend their learning in personally meaningful ways. Support experimentation and risk-taking in a safe learning environment.

### B. Presentation Techniques

- **Transitions**
   Implement clear verbal cues that signal shifts between concepts or activities. These cues help students maintain orientation and prepare for new information. Design visual transition elements that support cognitive processing and maintain engagement. These elements should be consistent throughout your content to establish familiar patterns.

   Create concept maps that show relationships between different topics and ideas. These maps help students understand how current learning connects to broader concepts. Use progress indicators that help students track their advancement through the material. These indicators should provide a sense of accomplishment and motivation.

- **Multiple Representations**
   Combine text and graphics effectively to convey information through multiple channels. This combination should be purposeful and coordinated to enhance understanding. Integrate audio and visual elements that complement each other and reinforce key concepts. Ensure these elements work together without creating cognitive overload.

   Develop interactive elements that encourage active engagement with the content. These elements should provide immediate feedback and support learning objectives. Include physical demonstrations when appropriate to illustrate concepts in tangible ways. These demonstrations should be clear, visible, and directly relevant to learning goals.

## 4. Assessment Integration

### A. Knowledge Verification
- **Formative Assessment**
   Implement regular quick checks for understanding throughout the learning process. These checks should be low-stakes and provide immediate feedback to both learner and instructor. Design self-assessment prompts that encourage students to reflect on their own learning progress. These prompts should help students develop metacognitive skills and self-awareness.

   Create opportunities for peer discussion and feedback that deepen understanding through explanation and debate. These discussions should be structured to ensure productive exchanges and learning outcomes. Develop reflection questions that help students connect new learning to existing knowledge and future applications. These questions should promote deep thinking and personal connection to the material.

- **Summative Assessment**
   Design project-based assessments that evaluate comprehensive understanding and practical application. These projects should integrate multiple concepts and skills learned throughout the course. Guide students in developing portfolios that demonstrate their learning journey and achievements. These portfolios should include examples of both process and product.

   Create opportunities for skill demonstration that allow students to show mastery in authentic contexts. These demonstrations should reflect real-world applications and standards. Develop knowledge application assessments that require students to transfer learning to new situations. These assessments should evaluate both understanding and adaptability.

### B. Learning Reinforcement
- **Review Strategies**
   Implement spaced repetition techniques that optimize long-term retention of information. This approach should strategically revisit concepts at increasing intervals. Create concept mapping exercises that help students visualize and understand relationships between ideas. These maps should become increasingly complex as understanding develops.

   Guide students in knowledge synthesis activities that combine multiple concepts into coherent understanding. These activities should help students see the bigger picture and make meaningful connections. Design application scenarios that require students to apply knowledge in new and challenging contexts. These scenarios should build confidence and demonstrate practical relevance.

## 5. Technical Considerations

### A. Video Production Elements
- **Duration Guidelines**
   Optimize video length to maintain engagement while effectively covering necessary content. The ideal duration of 6-12 minutes balances attention span with comprehensive coverage. Implement concept-based segmentation that breaks longer topics into digestible chunks. This segmentation should follow natural breaking points in the material.

   Consider attention span patterns when planning content structure and pacing. Include variety and interaction to maintain engagement throughout longer sessions. Adapt content length to platform-specific requirements and viewing habits. Consider mobile viewing habits and platform limitations in your planning.

- **Quality Standards**
   Ensure professional audio quality through proper equipment and recording techniques. This includes clear voice recording, minimal background noise, and appropriate volume levels. Maintain consistent lighting that enhances visibility and reduces viewer fatigue. Pay attention to both subject lighting and screen content visibility.

   Create clear visual presentations that effectively communicate key concepts. This includes appropriate font sizes, color contrast, and visual hierarchy. Maintain appropriate pacing that allows for processing time while maintaining engagement. Consider your audience's needs and learning objectives when determining pace.

### B. Accessibility Features
- **Universal Design**
   Create content that accommodates multiple learning modalities and preferences. This includes providing information through visual, auditory, and interactive channels. Ensure screen reader compatibility by following accessibility best practices and standards. This includes proper heading structure and alt text for images.

   Implement appropriate color contrast considerations for all visual elements. This ensures content is accessible to viewers with various visual abilities. Provide alternative text descriptions for all important images and graphics. These descriptions should convey the same information as the visual elements.

## 6. Follow-up Resources

### A. Supporting Materials
- **Resource Types**
   Develop comprehensive practice exercises that reinforce learning and build confidence. These exercises should range from basic to advanced, accommodating different skill levels. Create well-documented code samples that demonstrate best practices and common patterns. These samples should include comments explaining key concepts and decisions.

   Compile detailed reference guides that support independent learning and problem-solving. These guides should be easily searchable and regularly updated. Design cheat sheets that provide quick access to essential information and common procedures. These should be concise while including all crucial information.

### B. Implementation Guide
- **Learning Pathways**
   Create clear prerequisite maps that show relationships between different topics and skills. This mapping helps students understand learning dependencies and plan their progress. Provide advanced topic suggestions that help motivated learners extend their knowledge. These suggestions should include resources and guidance for self-directed learning.

   Develop skill progression guides that show clear paths from beginner to advanced levels. These guides should include milestones and checkpoints for measuring progress. Suggest project ideas that allow practical application of learned skills. These projects should be scalable to different skill levels and interests."""

_prompt_fix_error = """You are an expert Manim developer specializing in debugging and error resolution. Based on the provided implementation plan and Manim code, analyze the error message to provide a comprehensive fix and explanation.

Implementation Plan of the Scene:
{implementation_plan}

Manim Code:
```python
{manim_code}
```

Error Message:
{error_message}

Requirements:
1. Provide complete error analysis with specific line numbers where possible.
2. Include exact instructions for every code change.
3. Explain why the error occurred in plain language.
4. If external assets (e.g., images, audio, video) are referenced, remove them.
5. **If voiceover is present in the original code, ensure it remains preserved in the corrected code.**
6. Preserve all original code that is not causing the reported error. Do not remove or alter any intentional elements unnecessarily.
7. Follow best practices for code clarity and the current Manim version.

You MUST only output the following format (from <THINKING> to </FULL_CORRECTED_CODE>). You MUST NOT come up with any other format like JSON.

<THINKING>
Error Type: [Syntax/Runtime/Logic/Other]
Error Location: [File/Line number/Component]
Root Cause: [Brief explanation of what caused the error]
Impact: [What functionality is affected]
Solution:
[FIXES_REQUIRED]
- Fix 1: [Description]
  - Location: [Where to apply]
  - Change: [What to modify]
- Fix 2: [If applicable]
...
</THINKING>
<FULL_CORRECTED_CODE>
```python
# Complete corrected and fully implemented Python code
# Include all necessary imports, definitions, and any additional code for the script to run successfully
```
</FULL_CORRECTED_CODE>"""

_prompt_animation_simple = """Given a topic and the context, you need to explain the topic by text.

Also generate a Manim script that visually illustrates a key aspect of {topic} without including explanatory text in the animation itself.
Your text can mention the animation, but it should not be the main focus.
Context about the topic {topic}: {description}.

The animation should focus on:
* Illustrating the significant part of the theorem or concept – Use geometric figures, graphs, number lines, or any relevant visualization.
* Providing an intuitive example – Instead of proving the theorem, show a concrete example or transformation that visually supports understanding.
* Separately, provide a written explanation of the theorem as text that can be displayed outside the animation.

Ensure that:

* The animation is concise.
* The Manim code is compatible with the latest version of community manim.
* The visual elements are clear and enhance understanding.

Please provide the only output as:

1. A text explanation of the theorem.
2. A complete Manim script that generates the animation. Only give the code.

Output format:

(Text Explanation Output)
--- (split by ---)
(Manim Code Output)

Please do not include any other text or headers in your output.
Only use one --- to split the text explanation and the Manim code."""

_prompt_animation_rag_query_generation_fix_error = """You are an expert in Manim (Community Edition) and its plugins. Your task is to transform a complete implementation plan for a Manim animation scene into queries that can be used to retrieve relevant documentation from both Manim core and any relevant plugins. The implementation plan will describe the scene's vision, technical implementation, and animation strategy.

Here is the Text Explanation (Implementation Plan) as the context:

{text_explanation}

The error message will describe a problem encountered while running Manim code. Your queries should include keywords related to the specific Manim classes, methods, functions, and *concepts* that are likely related to the error, including any plugin-specific functionality. Focus on extracting the core concepts, actions, and vocabulary from the error message itself and the code snippet that produced the error. Generate queries that are concise and target different aspects of the documentation (class reference, method usage, animation examples, conceptual explanations) across both Manim core and relevant plugins.

Here is the error message and the code snippet:

**Error Message:**
{error}

**Code Snippet:**
{code}

Based on the error message and the code snippet, generate multiple human-like queries (maximum 5-7) for retrieving relevant documentation to fix this error. Please ensure that the search targets are different so that the RAG can retrieve a diverse set of documents covering various aspects of the error and its potential solutions.

**Specifically, ensure that:**
1. At least 1-2 queries are focused on retrieving information about Manim *function or class usage* that might be causing the error.
2. If the error message or code suggests the use of plugin functionality, include at least 1 query specifically targeting plugin documentation related to the error.
3. Queries should be specific enough to distinguish between core Manim and plugin functionality when relevant.

Output the queries in the following format:
[
    {{"query": "content of query 1", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 2", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 3", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 4", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 5", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 6", "type": "manim_core/name_of_the_plugin"}},
    {{"query": "content of query 7", "type": "manim_core/name_of_the_plugin"}},
] """

_prompt_animation_fix_error = """You are an expert Manim developer specializing in debugging and error resolution. Analyze the provided code and error message to provide a comprehensive fix and explanation.

<CONTEXT>
Text Explanation:
{text_explanation}

Manim Code Animation to complement the Text Explanation:
```python
{manim_code}
```

Error Message on code running:
{error_message}
</CONTEXT>

You MUST only output the following format (make sure to include the ```python and ``` in the code):

<ERROR_ANALYSIS>
Error Type: [Syntax/Runtime/Logic/Other]
Error Location: [File/Line number/Component]
Root Cause: [Brief explanation of what caused the error]
Impact: [What functionality is affected]
</ERROR_ANALYSIS>

<SOLUTION>
[FIXES_REQUIRED]
- Fix 1: [Description]
  - Location: [Where to apply]
  - Change: [What to modify]
- Fix 2: [If applicable]
  ...

[CORRECTED_CODE]
```python
# Complete corrected and fully implemented code, don't be lazy
# Include all necessary imports, definitions, and any additional code for the script to run successfully
```

</SOLUTION>

Requirements:
1. Provide complete error analysis with specific line numbers where possible.
2. Include exact instructions for every code change.
3. Ensure that the [CORRECTED_CODE] section contains complete, executable Python code (not just code snippets). Do not assume context from the prompt.
4. Explain why the error occurred in plain language.
5. Include verification steps to confirm the error is resolved.
6. Suggest preventive measures for avoiding similar errors in the future.
7. If external assets (e.g., images, audio, video) are referenced, remove them.
8. Preserve all original code that is not causing the reported error. Do not remove or alter any intentional elements unnecessarily.
9. Follow best practices for code clarity and the current Manim version."""

_prompt_scene_technical_implementation = """You are an expert in educational video production and Manim (Community Edition), adept at translating pedagogical narration plans into robust and spatially accurate Manim code.  
**Reminder:** This technical implementation plan is fully self-contained. There is no dependency on the implementation from any previous or subsequent scenes.

Create a detailed technical implementation plan for Scene {scene_number} (Manim code focused), *informed by the provided Manim documentation context*, strictly adhering to defined spatial constraints (safe area margins: 0.5 units, minimum spacing: 0.3 units), and **addressing potential text bounding box overflow issues**.

Topic: {topic}
Description: {description}

Scene Overview:
{scene_outline}

Scene Vision and Storyboard:
{scene_vision_storyboard}

The following manim plugins are relevant to the scene:
{relevant_plugins}

**Spatial Constraints (Strictly Enforced):**
*   **Safe area margins:** 0.5 units on all sides from the scene edges.  All objects must be positioned within these margins.
*   **Minimum spacing:** 0.3 units between any two Manim objects (measured edge to edge). This prevents overlaps and maintains visual clarity.

**Positioning Requirements:**
1.  All positioning MUST be relative (`next_to`, `align_to`, `shift`) from ORIGIN, safe margins, or other objects. **No absolute coordinates are allowed.**
2.  Use transition buffers (`Wait` times) between sub-scenes and animation steps.

**Diagrams/Sketches (Highly Recommended):**
*   Include diagrams/sketches (even text-based) for complex layouts to visualize spatial relationships, improve clarity, and reduce spatial errors.

**Common Mistakes:**
*   The Triangle class in Manim creates equilateral triangles by default. To create a right-angled triangle, use the Polygon class instead.

**Manim Plugins:**
*   You may use established, well-documented Manim plugins if they offer significant advantages in terms of code clarity, efficiency, or functionality not readily available in core Manim.
*   **If a plugin is used:**
    *   Clearly state the plugin name and version (if applicable).
    *   Provide a brief justification for using the plugin (e.g., "Using `manim-plugin-name` for its advanced graph layout capabilities").
    *   Ensure all plugin usage adheres to the plugin's documentation.
    *   Include a comment in the plan: `### Plugin: <plugin_name> - <brief justification>`.

**Focus:**
*   Creating *pedagogically sound and spatially correct Manim code*.
*   Detailed technical descriptions, referencing Manim documentation.
*   Strict adherence to spatial constraints and relative positioning.

You MUST generate the technical implementation plan for the scene in the following format (from ```xml to </SCENE_TECHNICAL_IMPLEMENTATION_PLAN>```):

```xml
<SCENE_TECHNICAL_IMPLEMENTATION_PLAN>
0. **Dependencies**:
    - **Manim API Version**: Target the latest stable Manim release, using only documented API elements.
    - **Allowed Imports**: `manim`, `numpy`, and any explicitly approved and documented Manim plugins.  No external assets (e.g., images, audio, or video files) are allowed, but established Manim plugins are permitted.
    
1. **Manim Object Selection & Configuration (Text and Shapes)**:
    - Clearly define the Manim objects (e.g., `Tex`, `MathTex`, `Circle`, `Line`, etc.) used to construct the scene.  Also include any objects provided by used plugins.
    - Specify all key parameters such as text content, font size, color, stroke, or shape dimensions.
    - **Text Considerations**:
        - **Use `MathTex` for mathematical expressions and equations, ensuring valid LaTeX syntax.** For example: `MathTex("x^2 + y^2 = r^2")`.
        - **Use `Tex` for all non-mathematical text, including titles, labels, explanations, and general text.** For example: `Tex("This is a circle")`.
        - **If you need to include regular text *within* a `MathTex` environment (e.g., for explanations alongside a formula), use the `\\text{{}}` command.** For example: `MathTex(r"\\text{{Area of circle}} = \\pi r^2")`.
        - **Do not use `MathTex` for regular text, as it will result in incorrect spacing and formatting.**
        - **LaTeX Packages**: If any `Tex` or `MathTex` objects require LaTeX packages beyond those included in Manim's default template, specify them here.  For example: "Requires: `\\usepackage{{amssymb}}`".  Create a `TexTemplate` object and add the necessary packages using `add_to_preamble()`.
        - **Font Size Recommendations**:
            - If there is title text, font size is highly recommended to be 28.
            - If there are side labels or formulas, font size is highly recommended to be 24.
            - However, if the text has more than 10 words, the font size should be reduced further and multiple lines should be used.
    - Confirm all objects begin within the safe area (0.5 units from all edges) and maintain at least 0.3 units spacing to avoid overlaps.
    
2. **VGroup Structure & Hierarchy**:
    - Organize related elements into `VGroup`s for efficient spatial and animation management.  If a plugin provides a specialized group-like object, consider using it.
    - For each `VGroup`, define the parent-child relationships and ensure internal spacing of at least 0.3 units.
    - Clearly document the purpose for each grouping (e.g., "formula_group" for mathematical expressions).
    
3. **Spatial Positioning Strategy**:
    - Mandate the exclusive use of relative positioning methods (`next_to`, `align_to`, `shift`), based on ORIGIN, safe margins, or other objects.
    - For every object, specify:
        - The reference object (or safe edge) used for positioning.
        - The specific method (and direction/aligned edge) along with a `buff` value (minimum 0.3 units).
    - Outline the layout in sequential stages, inserting visual checkpoints to verify that every element continues to respect safe margins and spacing.
    - Highlight measures to safeguard text bounding boxes, especially for multi-line text.
    - Reference the font size recommendations under "Text Considerations" to ensure appropriate sizing and prevent overflow.
    
4. **Animation Methods & Object Lifecycle Management**:
    - Define clear animation sequences using documented methods such as `Create`, `Write`, `FadeIn`, `Transform`, and corresponding removal animations (`FadeOut`, `Uncreate`). Include animation methods from plugins if they are used.
    - For each animation, specify parameters like `run_time`, `lag_ratio`, and the use of `Wait()` for transition buffers.
    - Ensure every object's appearance and removal is managed to prevent clutter and maintain scene clarity.
    
5. **Code Structure & Reusability**:
    - Propose modular functions for creating and animating common objects to promote code reusability.
    - Organize the overall code structure into logical sections: dependencies, object definitions, individual layout stages, and the main `construct` method.
    - Include inline comments to document the rationale for configuration choices, referencing the Manim Documentation *and the plugin documentation where applicable*.
    
***Mandatory Safety Checks***:
    - **Safe Area Enforcement**: All objects, including text bounding boxes, must remain within 0.5 unit margins.
    - **Minimum Spacing Validation**: Confirm a minimum of 0.3 units spacing between every pair of objects.
    - **Transition Buffers**: Use explicit `Wait()` calls to separate animation steps and sub-scenes.
</SCENE_TECHNICAL_IMPLEMENTATION_PLAN>
```
"""

_prompt_rag_query_generation_narration = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to analyze a storyboard and generate effective queries that will retrieve relevant documentation about narration, text animations, and audio-visual synchronization.

Here is the storyboard:

{storyboard}

Based on this storyboard, generate multiple human-like queries (maximum 10) for retrieving relevant documentation about narration and text animation techniques.

**Specifically, ensure that:**
1. Queries focus on retrieving information about **text animations** and their properties
2. Include queries about **timing and synchronization** techniques
3. If the storyboard suggests using plugin functionality, include specific queries targeting those plugin's narration capabilities

The above storyboard is relevant to these plugins: {relevant_plugins}.
Note that you MUST NOT use the plugins that are not listed above.

You MUST only output the queries in the following JSON format (with json triple backticks):
```json
[
    {{"type": "manim-core", "query": "content of text animation query"}},
    {{"type": "<plugin-name>", "query": "content of plugin-specific query"}},
    {{"type": "manim-core", "query": "content of timing synchronization query"}}
    ...
]
```"""

_prompt_context_learning_animation_narration = """Here are some example animation and narration plans to help guide your planning:

{examples}

Please follow a similar structure while maintaining creativity and relevance to the current scene."""

_prompt_scene_implementation = """You are an expert in educational video production and Manim (Community Edition) animation development. Your task is to create a detailed implementation plan for Scene {scene_number}.

<BASE_INFORMATION>
Topic: {topic}
Description: {description}
</BASE_INFORMATION>

<SCENE_CONTEXT>
Scene Overview:
{scene_outline}
</SCENE_CONTEXT>

<IMPLEMENTATION_PLAN>

[SCENE_VISION]
1.  **Overall Narrative**:
    - Describe the overall story or message of the scene. What is the key takeaway for the viewer?
    - How does this scene fit into the larger narrative of the video?
    - What is the desired emotional impact on the viewer?

2.  **Learning Objectives**:
    - What specific knowledge or skills should the viewer gain from this scene?
    - How will the visual elements and animations support these learning objectives?
    - What are the key concepts that need to be emphasized?

[STORYBOARD]
1.  **Visual Flow**:
    - Describe the sequence of visual elements and animations in the scene.
    - Provide a rough sketch or description of the key visual moments.
    - How will the scene transition between different ideas or concepts?
    - What is the pacing of the scene? Are there moments of pause or rapid action?

[TECHNICAL_IMPLEMENTATION]
1.  **High-Level Components (VGroups)**:
    - **Identify the main conceptual sections of the scene.** Think of this like outlining chapters in a story or sections in a presentation.
    - **Define the purpose of each high-level component.** What should the viewer learn or understand from each section?
    - **Describe how these components relate to each other and the overall scene flow.** How will you transition between these sections to create a cohesive narrative?
    - **Provide a brief rationale for your choice of high-level components.** Why did you choose these specific sections?

2.  **VGroup Hierarchy**:
    - **For each high-level component, define a parent VGroup.** This VGroup will act as a container for all elements within that section.
    - **Break down each parent VGroup into nested VGroups for sub-components as needed.** Think about logical groupings of elements.
    - **Specify the relative positioning of these VGroups within the scene using `next_to()`, `align_to()`, and `shift()` where possible.** How will the parent VGroups be arranged on the screen relative to each other? (e.g., stacked vertically, side-by-side, etc.) Prioritize relative positioning using the following references:
        - `ORIGIN`: the center of the scene
        - scene margins (e.g., corners, edges)
        - other VGroups as references.
        - **MUST NOT use absolute coordinates.**
    - **Define the scale relationships between different levels of the VGroup hierarchy.** Will sub-VGroups inherit scale from parent VGroups? How will scaling be managed to maintain visual consistency?
    - **Provide a brief rationale for your VGroup hierarchy.** Why did you choose this specific structure?

    For each VGroup level (from high-level down to sub-components):
    - Name: [Descriptive name for the VGroup, e.g., "TitleSection", "ProblemStatementGroup", "Explanation1Group"]
    - Purpose: [What is the purpose of this VGroup? What should the viewer learn or understand from this VGroup?]
    - Contents: [List all child VGroups and individual elements (Text, MathTex, Shapes, etc.) that belong to this VGroup.]
    - Positioning:
        * Reference: [Specify what this VGroup is positioned relative to. Do not use absolute coordinates.]
        * Alignment: [How is it aligned relative to the reference? Use `align_to()` with options like `UP`, `DOWN`, `LEFT`, `RIGHT`, `ORIGIN`, etc.]
        * Spacing: [Describe any spacing considerations relative to sibling VGroups or elements within the parent. Use `buff` argument in `next_to()` or `arrange()`. Refer to the defined minimum spacing value.]
    - Scale: [Specify the scale of this VGroup relative to its parent VGroup. Use relative scaling factors (e.g., 1.0 for same scale, 0.8 for smaller).]
    - Rationale: [Explain the reasoning behind the structure and organization of this VGroup. Why did you group these elements together?]

3.  **Element Specification**:
    For each individual element (Text, MathTex, Shapes, etc.) within a VGroup:
    - Name: [Descriptive name for the element, e.g., "ProblemTitleText", "Equation1", "HighlightCircle"]
    - Type: [Manim object type. Examples: Text, MathTex, Circle, Rectangle, Arrow, Line, etc.]
    - Parent VGroup: [Specify the VGroup this element belongs to. This establishes the hierarchical relationship.]
    - Positioning:
        * Reference: [Specify what this element is positioned relative to. Use its parent VGroup, other elements, `ORIGIN`, or scene margins as references. Do not use absolute coordinates.]
        * Alignment: [How is it aligned within its parent VGroup? Use `align_to()` or `next_to()` with appropriate directions, e.g. `UP`, `DOWN`, `LEFT`, `RIGHT`, `ORIGIN`, `UL`, `UR`, `DL`, `DR`]
        * Spacing: [If applicable, describe spacing relative to other elements using `buff` in `next_to()`. Refer to the defined minimum spacing value.]
    - Style Properties:
        * Color: [Hex code or named color (e.g., "RED", "BLUE"). Use hex codes for specific colors. e.g., #FF0000 for red]
        * Opacity: [Value between 0 and 1. 1 for fully opaque, 0 for fully transparent.]
        * Stroke Width: [Specify stroke width using levels: `thin`, `medium`, or `thick`.]
        * Font: [Font family name, if applicable.]
        * Font Size: [Specify font size using levels: `heading1`, `heading2`, `heading3`, `heading4`, `heading5`, `heading6`, or `body`. Refer to the defined font size levels.]
        * Fill Color: [Hex code for fill color, if applicable.]
        * ... [Include any other relevant style properties]
    - Z-Index: [Integer value for layering order within the VGroup. Higher values are on top.]
    - Required Imports: [List specific Manim classes that need to be imported to create this element. e.g., `from manim import Text, Circle`]

[ANIMATION_STRATEGY]
1.  **VGroup Transitions**:
    - **Define how parent VGroups will transition onto and off of the scene, and between different sections.** Describe the movement patterns for these high-level groups. Examples: 'Slide in from left', 'Fade in and scale up', 'Move to top of screen'.
    - **Specify the timing and coordination of VGroup transitions.** How long will each transition take? Will transitions overlap or be sequential?
    - **Describe any transformation sequences applied to VGroups during transitions.** Will VGroups rotate, scale, or change shape during transitions?

2.  **Element Animations**:
    - **Define the animations for individual elements within each VGroup.** What animations will bring each element to life? Examples: 'Write in text', 'Draw a circle', 'Highlight an equation', 'Fade in an image'.
    - **Group related element animations using Manim's animation grouping features (e.g., `AnimationGroup`, `Succession`).** Explain how these groups will be used to create cohesive animation sequences.
    - **Coordinate element animations with parent VGroup movements and transitions.** Ensure element animations are synchronized with the overall scene flow.
    - **Specify the timing of element animations relative to VGroup transitions and other element animations.** Create a timeline or sequence of animations.

3.  **Scene Flow**:
    - **Describe the overall animation sequence for the entire scene.** Outline the order in which VGroups and elements will be animated.
    - **Specify transition buffers or pauses between major sections of the scene.** How much time will be left between animations for the viewer to process information?
    - **Consider how the animation timing will coordinate with the narration (if narration is planned).** Animations should complement and reinforce the spoken content.

[NARRATION]
- **Narration Script:** [Provide the full script for the narration, including timing cues or markers for when specific animations should occur. The script should be clear, detailed, and engaging, and should align with the visual elements and animations.]
- **Narration Sync:** [Describe how the narration should be synchronized with the animations. Specify how timing cues in the narration script will be used to trigger animations. Are there specific points where the narration and animations should be perfectly synchronized? Explain how you will achieve this synchronization.]

[VIEWER_EXPERIENCE]
1.  **Cognitive Load**:
    - How will you manage the amount of information presented at any given time?
    - Are there any complex concepts that need to be broken down into smaller steps?
    - How will you use visual cues to guide the viewer's attention?

2.  **Pacing**:
    - Is the pacing of the scene appropriate for the content?
    - Are there moments where the viewer needs time to pause and reflect?
    - How will you use animation timing to control the pace of the scene?

3.  **Accessibility**:
    - How will you ensure that the scene is accessible to viewers with different needs?
    - Are there any specific considerations for color contrast or text readability?

[TECHNICAL_CHECKS]
- **VGroup boundary validation:** Ensure all elements are contained within their intended VGroup boundaries and are not overflowing unexpectedly.
- **Hierarchy scale consistency:** Verify that scaling is applied consistently throughout the VGroup hierarchy and that text and elements remain readable at all scales.
- **Animation coordination between levels:** Check that animations at different VGroup levels are coordinated and do not clash or look disjointed.
- **Performance optimization for nested groups:** Consider the performance implications of deeply nested VGroups and optimize structure and animations for smooth playback.
- **Text readability:** Ensure all text elements are legible in terms of size, color contrast, and positioning.
- **Color contrast:** Verify sufficient color contrast between text and background, and between different visual elements for accessibility.
- **Animation smoothness:** Check for any jerky or abrupt animations and refine timing and easing for smoother transitions.

</IMPLEMENTATION_PLAN>

Requirements:
1. All elements must stay within safe area margins
2. Maintain minimum spacing between objects: [value]  (This value is defined in the project settings)
3. Use relative positioning when possible, leveraging `next_to()`, `align_to()`, and `shift()`. Only reference positions relative to `ORIGIN`, scene margins, or other object reference points. Do not use absolute coordinates.
4. Include transition buffers between animations
5. Specify z-index for overlapping elements
6. All colors must use hex codes or named colors
7. Define scale relative to base unit
8. No external dependencies
9. Currently, there are no images or other assets available locally or remotely for you to use in the scene. Only include elements that can be generated through manim.
10. **Do not generate any code in this plan, except for illustrative examples where necessary. This plan is for outlining the scene and should not include any python code.**
11. **The purpose of this plan is to be a detailed guide for a human to implement the scene in manim.**"""

_prompt_visual_fix_error = """You are an expert in Manim animations. Your task is to ensure that the rendered animation frame (image) aligns with the intended teaching content based on the provided implementation plan.

Instructions:
Evaluate whether the object coordinates and positions in the image match the described plan and educational purpose.
The implementation plan serves as a reference, but your primary goal is to verify that the rendered animation frame supports effective teaching.
For example:
* If the object is supposed to be at the top of the screen, but it is at the bottom, you need to adjust the position.
* If the object is supposed to be at the left side but it is too far to the left, you need to adjust the position.
* If the two objects are not supposed to be overlapped but it is overlapped, you need to adjust the positions.

If adjustments are needed, provide the complete code of the adjusted version.
If the current code is correct, return it as is.

Manim Implementation Plan:
{implementation}

Generated Code:
{generated_code}

Return the complete code of the adjusted version if the code needs to be updated. If the code is correct, only return "<LGTM>" as output.
"""

_banned_reasonings = """evaluation cannot
can't assist
cannot assist
can't provide
cannot provide
can't evaluate
cannot evaluate
cannot be evaluated
cannot be rated
cannot be completed
cannot be assessed
cannot be scored
cannot be conducted
unable to evaluate
do not have the capability
do not have the ability
are photographs and not AI-generated
unable to provide the evaluation"""

_prompt_code_generation = """You are an expert Manim (Community Edition) developer for educational content. Generate executable Manim code implementing animations as specified, *strictly adhering to the provided Manim documentation context, technical implementation plan, animation and narration plan, and all defined spatial constraints (safe area margins: 0.5 units, minimum spacing: 0.3 units)*.

Think of reusable animation components for a clean, modular, and maintainable library, *prioritizing code structure and best practices as demonstrated in the Manim documentation context*. *Throughout code generation, rigorously validate all spatial positioning and animations against the defined safe area margins and minimum spacing constraints. If any potential constraint violation is detected, generate a comment in the code highlighting the issue for manual review and correction.*

Input Context:

Topic: {topic}
Description: {description}

Scene Outline:
{scene_outline}

Scene Technical Implementation:
{scene_implementation}

**Code Generation Guidelines:**

1.  **Scene Class:** Class name `Scene{scene_number}`, where `{scene_number}` is replaced by the scene number (e.g., `Scene1`, `Scene2`). The scene class should at least inherit from `VoiceoverScene`. However, you can add more Manim Scene classes on top of VoiceoverScene for multiple inheritance if needed.
2.  **Imports:** Include ALL necessary imports explicitly at the top of the file, based on used Manim classes, functions, colors, and constants. Do not rely on implicit imports. Double-check for required modules, classes, functions, colors, and constants, *ensuring all imports are valid and consistent with the Manim Documentation*.  **Include imports for any used Manim plugins.**
3.  **Speech Service:** Initialize speech service using `get_speech_service()`. You MUST import like this: `from src.utils.elevenlabs_voiceover import get_speech_service` as this is our custom voiceover service that conditionally enables voice generation.
4.  **Reusable Animations:** Implement functions for each animation sequence to create modular and reusable code. Structure code into well-defined functions, following function definition patterns from Manim Documentation.
5.  **Voiceover:** Use `with self.voiceover(text="...")` for speech synchronization, precisely matching the narration script and animation timings from the Animation and Narration Plan.
6.  **Comments:** Add clear and concise comments for complex animations, spatial logic (positioning, arrangements), and object lifecycle management. *Use comments extensively to explain code logic, especially for spatial positioning, animation sequences, and constraint enforcement, mirroring commenting style in Manim Documentation*.  **Add comments to explain the purpose and usage of any Manim plugins.**
7.  **Error Handling & Constraint Validation:** Implement basic error handling if error handling strategies are suggested or exemplified in the Manim Documentation. **Critically, during code generation, implement explicit checks to validate if each object's position and animation adheres to the safe area margins (0.5 units) and minimum spacing (0.3 units).**
8.  **Performance:** Follow Manim best practices for efficient code and rendering performance, as recommended in the Manim Documentation.
9.  **Manim Plugins:** You are allowed and encouraged to use established, well-documented Manim plugins if they simplify the code, improve efficiency, or provide functionality not readily available in core Manim.
    *   **If a plugin is used:**
        *   Include the necessary import statement at the top of the file.
        *   Add a comment indicating the plugin used and its purpose: `### Plugin: <plugin_name> - <brief justification>`.
        *   Ensure all plugin usage adheres to the plugin's documentation.
10. **No External Assets:** No external files (images, audio, video). *Use only Manim built-in elements and procedural generation, or elements provided by approved Manim plugins. No external assets are allowed*.
11. **No Main Function:** Only scene class. No `if __name__ == "__main__":`.
12. **Spatial Accuracy (Paramount):** Achieve accurate spatial positioning as described in the technical implementation plan, *strictly using relative positioning methods (`next_to`, `align_to`, `shift`, VGroups) and enforcing safe area margins and minimum 0.3 unit spacing, as documented in Manim Documentation Context*. *Spatial accuracy and constraint adherence are the highest priorities in code generation.*
13. **VGroup Structure:** Implement VGroup hierarchy precisely as defined in the Technical Implementation Plan, using documented VGroup methods for object grouping and manipulation.
14. **Spacing & Margins (Strict Enforcement):** Adhere strictly to safe area margins (0.5 units) and minimum spacing (0.3 units) requirements for *all* objects and VGroups throughout the scene and all animations. Prevent overlaps and ensure all objects stay within the safe area. *Rigorously enforce spacing and margin requirements using `buff` parameters, relative positioning, and explicit constraint validation checks during code generation, and validate against safe area guidelines from Manim Documentation Context*.
15. **Background:** Default background (Black) is sufficient. Do not create custom color background Rectangles.
16. **Text Color:** Do not use BLACK color for any text. Use predefined colors (BLUE_C, BLUE_D, GREEN_C, GREEN_D, GREY_A, GREY_B, GREY_C, LIGHTER_GRAY, LIGHT_GRAY, GOLD_C, GOLD_D, PURPLE_C, TEAL_C, TEAL_D, WHITE).
17. **Default Colors:** You MUST use the provided color definitions if you use colors in your code. ONLY USE THE COLORS PREVIOUSLY DEFINED.
18. **Animation Timings and Narration Sync:** Implement animations with precise `run_time` values and synchronize them with the narration script according to the Animation and Narration Plan. Use `Wait()` commands with specified durations for transition buffers.
19. **Don't be lazy on code generation:** Generate full, complete code including all helper functions. Ensure that the output is comprehensive and the code is fully functional, incorporating all necessary helper methods and complete scene implementation details.
20. **LaTeX Package Handling:** If the technical implementation plan specifies the need for additional LaTeX packages:
    *   Create a `TexTemplate` object.
    *   Use `myTemplate = TexTemplate()`
    *   Use `myTemplate.add_to_preamble(r"\\usepackage{{package_name}}")` to add the required package.
    *   Pass this template to the `Tex` or `MathTex` object: `tex = Tex(..., tex_template=myTemplate)`.

**Example Code Style and Structure to Emulate:**

*   **Helper Classes:** Utilize helper classes (like `Scene2_Helper`) to encapsulate object creation and scene logic, promoting modularity and reusability.
*   **Stage-Based `construct` Method:** Structure the `construct` method into logical stages (e.g., Stage 1, Stage 2, Stage 3) with comments to organize the scene flow.
*   **Reusable Object Creation Functions:** Define reusable functions within helper classes for creating specific Manim objects (e.g., `create_axes`, `create_formula_tex`, `create_explanation_text`).
*   **Clear Comments and Variable Names:** Use clear, concise comments to explain code sections and logic. Employ descriptive variable names (e.g., `linear_function_formula`, `logistic_plot`) for better readability.
*   **Text Elements:** Create text elements using `Tex` or `MathTex` for formulas and explanations, styling them with `color` and `font_size` as needed.
*   **Manim Best Practices:** Follow Manim best practices, including using `VoiceoverScene`, `get_speech_service()`, common Manim objects, animations, relative positioning, and predefined colors.

You MUST generate the Python code in the following format (from <CODE> to </CODE>):
<CODE>
```python
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
class Scene{scene_number}_Helper:  # Example: class Scene1_Helper:
    # Helper class containing utility functions for scene {scene_number}.
    def __init__(self, scene):
        self.scene = scene
        # ... (add any necessary initializations)

    # Reusable object creation functions (Implement object creation functions for modularity and reusability as per plan)
    def get_center_of_edges(self, polygon, buff=SMALL_BUFF*3):
        # Calculate the center points of each edge in a polygon (Triangle, Square, etc.) with an optional buffer.
        # Get the vertices of the polygon
        vertices = polygon.get_vertices()
        n_vertices = len(vertices)
        # Initialize list to store edge centers
        coords_vertices = []
        # Calculate center point and normal for each edge
        for i in range(n_vertices):
            # Get current and next vertex (wrapping around to first vertex)
            v1 = vertices[i]
            v2 = vertices[(i + 1) % n_vertices]
            # Calculate edge center
            edge_center = (v1 + v2) / 2
            # Calculate edge vector and normalize
            edge_vector = v2 - v1
            edge_length = np.linalg.norm(edge_vector)
            normal = np.array([-edge_vector[1], edge_vector[0], 0]) / edge_length
            # Add buffer in the normal direction
            coords_vertices.append(edge_center + normal * buff)
        
        return coords_vertices
    
    def create_formula_tex(self, formula_str, color):
        # Example function to create a MathTex formula with a specified color.
        # Check if a custom TexTemplate is needed (from the technical plan).
        if hasattr(self.scene, 'tex_template'):
            formula = MathTex(formula_str, color=color, tex_template=self.scene.tex_template)
        else:
            formula = MathTex(formula_str, color=color)
        return formula

    # ... (add more helper functions as needed for object creation and scene logic)


class Scene{scene_number}(VoiceoverScene, MovingCameraScene):  # Note: You can add more Manim Scene classes on top of current templates for multiple inheritance if needed.
    # Reminder: This scene class is fully self-contained. There is no dependency on the implementation from previous or subsequent scenes.
    def construct(self):
        # Initialize speech service
        self.set_speech_service(get_speech_service())

        # Instantiate helper class (as per plan)
        helper = Scene{scene_number}_Helper(self)  # Example: helper = Scene1_Helper(self)

        # Check for LaTeX packages and create TexTemplate if needed.
        # This section should be generated based on the technical implementation plan.
        # For example, if the plan includes:  "Requires: \\usepackage{{amsmath}}"
        # Then generate:
        #
        # my_template = TexTemplate()
        # my_template.add_to_preamble(r"\\usepackage{{amsmath}}")
        # self.tex_template = my_template
        
        # --- Stage 1: Scene Setup (adapt stage numbers and descriptions to your scene, following plan) ---
        with self.voiceover(text="[Narration for Stage 1 - from Animation and Narration Plan]") as tracker:  # Voiceover for Stage 1
            # Object Creation using helper functions (as per plan)
            axes = helper.create_axes()  # Example: axes = helper.create_axes()
            formula = helper.create_formula_tex("...", BLUE_C)  # Example: formula = helper.create_formula_tex("...", BLUE_C)
            explanation = helper.create_explanation_text("...")  # Example: explanation = helper.create_explanation_text("...")

            # Positioning objects (relative positioning, constraint validation - as per plan)
            formula.to_corner(UL)  # Example positioning
            axes.move_to(ORIGIN)  # Example positioning
            explanation.next_to(axes, RIGHT)  # Example positioning

            # Animations for Stage 1 (synced with voiceover - as per plan)
            self.play(Write(formula), Write(axes), run_time=tracker.duration)  # Example animations
            self.wait(0.5)  # Transition buffer

        # --- Stage 2:  ... (Implement Stage 2, Stage 3, etc. in a similar modular and structured way, following plan) ---
        with self.voiceover(text="[Narration for Stage 2 - from Animation and Narration Plan]") as tracker:  # Voiceover for Stage 2
            # ... (Object creation, positioning, and animations for Stage 2, using helper functions and constraint validation)
            pass  # Replace with actual Stage 2 code

        # ... (Implement remaining stages in a similar modular and structured way, following the Animation and Narration Plan and Technical Implementation Plan, and rigorously validating spatial constraints in each stage)

        self.wait(1)  # Scene end transition buffer
```
</CODE>

Notes:
The `get_center_of_edges` helper function is particularly useful for:
1. Finding the midpoint of polygon edges for label placement
2. Calculating offset positions for side labels that don't overlap with the polygon
3. Creating consistent label positioning across different polygon sizes and orientations

Example usage in your scene:
```python
def label_triangle_sides(self, triangle, labels=["a", "b", "c"]):
    # Helper function to label triangle sides.
    edge_centers = self.helper.get_center_of_edges(triangle)
    labeled_sides = VGroup()
    for center, label in zip(edge_centers, labels):
            tex = MathTex(label).move_to(center)
            labeled_sides.add(tex)
        return labeled_sides
```"""

_prompt_rag_query_generation_code = """You are an expert in generating search queries specifically for **Manim (Community Edition) documentation** (both core Manim and its plugins). Your task is to transform a complete implementation plan for a Manim video scene into effective queries that will retrieve relevant information from Manim documentation. The implementation plan describes the scene's vision, storyboard, technical implementation, and animation/narration strategy.

Here is the complete scene implementation plan:

{implementation_plan}

Based on the complete implementation plan, generate multiple human-like queries (maximum 10) for retrieving relevant documentation. Please ensure that the search targets are different so that the RAG can retrieve a diverse set of documents covering various aspects of the implementation.

**Specifically, ensure that:**
1.  At least some queries are focused on retrieving information about **Manim function usage** in scenes. Frame these queries to target function definitions, usage examples, and parameter details within Manim documentation.
2.  If the implementation suggests using plugin functionality, include at least 1 query specifically targeting **plugin documentation**.  Clearly mention the plugin name in these queries to focus the search.
3.  Queries should be specific enough to distinguish between core Manim and plugin functionality when relevant, and to target the most helpful sections of the documentation (API reference, tutorials, examples).

The above implementation plans are relevant to these plugins: {relevant_plugins}.
Note that you MUST NOT use the plugins that are not listed above.

You MUST only output the queries in the following JSON format (with json triple backticks):
```json
[
    {{"type": "manim-core", "query": "content of function usage query"}},
    {{"type": "<plugin-name>", "query": "content of plugin-specific query"}},
    {{"type": "manim-core", "query": "content of API reference query"}}
    ...
]
```"""

# Tavily-related prompts for advanced error-driven development
_prompt_tavily_search_query_generation = """You are an expert in analyzing Python error tracebacks, specifically for Manim (Community Edition) errors. Your task is to analyze a full, potentially verbose traceback and generate a concise, effective search query under 400 characters that will help find solutions online.

<CONTEXT>
Full Error Traceback:
{traceback}

Original Code Context:
{code_context}

Implementation Plan Context:
{implementation_plan}
</CONTEXT>

<TASK>
Analyze the provided traceback and generate the most effective search query to find a solution. Focus on:

1. **Error Type**: Identify the specific exception (AttributeError, TypeError, etc.)
2. **Key Components**: Extract the most important Manim classes, methods, or concepts
3. **Root Cause**: Determine what specifically went wrong
4. **Search Strategy**: Create a query that will find relevant documentation or solutions

**Important Constraints:**
- Query MUST be under 400 characters
- Focus on the most specific, actionable parts of the error
- Include "manim" as a keyword
- Prioritize technical terms over generic descriptions
</TASK>

<OUTPUT_FORMAT>
Search Query: [Your concise search query here - under 400 characters]

Query Rationale: [Brief explanation of why this query will be effective]

Key Error Components:
- Error Type: [The main exception type]
- Failed Component: [The specific Manim object/method that failed]
- Context: [Brief context about what was being attempted]
</OUTPUT_FORMAT>

**Examples of Good Queries:**
- "manim AttributeError SurroundingRectangle animate wiggle method"
- "manim TypeError Transform function object len"
- "manim ImportError missing manim community edition"

Generate your response following the OUTPUT_FORMAT exactly."""

_prompt_tavily_assisted_fix_error = """You are an expert Manim developer specializing in debugging and error resolution using web search insights. You have access to search results from Tavily that contain relevant information about the error. Use this information to provide a comprehensive fix.

<CONTEXT>
Implementation Plan:
{implementation_plan}

Original Manim Code:
```python
{manim_code}
```

Error Message:
{error_message}

Tavily Search Results:
{tavily_search_results}

Search Query Used: {search_query}
</CONTEXT>

<INSTRUCTIONS>
Using the Tavily search results and your expertise, analyze the error and provide a complete fix. The search results contain real-world solutions and documentation that should guide your fix approach.

**Priority Order for Solutions:**
1. Official Manim documentation insights
2. GitHub issues and solutions
3. Stack Overflow community solutions
4. Reddit/Discord community fixes
5. Your expert knowledge as fallback

**Key Requirements:**
- Extract actionable insights from the search results
- Apply modern Manim best practices
- Provide complete, executable code
- Explain the fix with reference to sources found
</INSTRUCTIONS>

You MUST output in the following format:

<TAVILY_INSIGHTS>
Key Findings from Search:
- [Insight 1 from search results]
- [Insight 2 from search results]
- [Insight 3 from search results]

Most Relevant Source: [URL or source that best addresses this error]
</TAVILY_INSIGHTS>

<ERROR_ANALYSIS>
Error Type: [Syntax/Runtime/Logic/Other]
Error Location: [File/Line number/Component]
Root Cause: [Brief explanation based on search insights]
Search-Informed Solution: [How the search results inform the fix]
</ERROR_ANALYSIS>

<SOLUTION>
[FIXES_APPLIED]
- Fix 1: [Description with reference to search source]
  - Source: [Which search result provided this insight]
  - Change: [What to modify]
- Fix 2: [If applicable]
  ...

[CORRECTED_CODE]
```python
# Complete corrected code based on Tavily search insights
# Comments explaining fixes with source references
```

[VERIFICATION_STEPS]
1. [Step to verify the fix works]
2. [Additional verification if needed]

[PREVENTION_TIPS]
- [How to avoid this error in future, based on search insights]
- [Best practices learned from search results]
</SOLUTION>

**Requirements:**
1. Reference specific search results when explaining fixes
2. Include source URLs when applicable
3. Ensure corrected code is complete and executable
4. Prioritize solutions from authoritative sources (official docs, maintainers)
5. If search results are insufficient, clearly state limitations"""

