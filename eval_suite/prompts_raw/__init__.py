# This file is generated automatically through parse_prompt.py

_video_eval_new = """# Task: Video Frame Quality Evaluation

You are tasked with analyzing and scoring a chunk of a theorem explanation video. Note that you may not have the full context of the video. Your job is to assign a score from 1 to 5 for each criterion. Please provide a brief justification for your scores.

## Evaluation Criteria

1. **Visual Consistency**
   - Style Consistency: Does the visual style remain consistent across frames?
   - Smoothness: Are the motions and transitions smooth?

## Scoring Instructions
1. Assign a score from **1 to 5** for each dimension:
   - **1**: Very poor quality, completely fails to meet the criteria.
   - **2**: Below average, significant issues present.
   - **3**: Acceptable, meets the basic criteria with minor issues.
   - **4**: Good, performs well with no major issues.
   - **5**: Excellent, fully meets or exceeds expectations.
2. Provide a comprehensive evaluation for each dimension.
3. Format your output in **JSON**

### JSON Output Format
```json
{{
  "overall_analysis": "[Provide a general assessment of the video's quality]",
  "evaluation": {{
    "visual_consistency": {{
      "comprehensive_evaluation": "[Analysis of visual consistency]",
      "score": [1-5]
    }}
  }}
}}
```

Description of the theorem:
{description}

Video chunk:"""

_text_eval_new = """You are a specialist in evaluating theorem explanation videos, known for giving clear and objective feedback. You will be given the transcript of a video. Your task is to evaluate and score the content of the video in several dimensions.

### Task Objective
1. Perform an overall analysis of the video.
    * Identify the topic of the video.
    * Note your general thoughts and impression of the video, and any findings and observations.
2. Conduct a comprehensive evaluation and score each criterion in the given dimensions.
    * Analyze how well or poorly the video meets each criterion.
    * Assign a score from **1 to 5** for each dimension:
        - **1**: Very poor quality, completely fails to meet the criteria.
        - **2**: Below average, significant issues present.
        - **3**: Acceptable, meets the basic criteria with minor issues.
        - **4**: Good, performs well with no major issues.
        - **5**: Excellent, fully meets or exceeds expectations.
3. Output the results in the specified JSON format.

### Evaluation Criteria
1. **Accuracy and Depth**
    - Does the narration explain the theorem accurately?
    - Does the video provide intuitive and/or rigorous explanations for why the theorem holds?
2. **Logical Flow**
    - Does the video follow a clear and logical structure?
    - Does the video present a coherent buildup of ideas?

### Notes
* You do not have access to the visual portion of the video as you are given only the textual portion. Do not reference or commentate on the visuals as they will be evaluated separately - just assume that there are reasonable visuals (e.g., geometric objects, graphs of functions, and calculations) to accompany the narration.
* The evaluation criteria are intended to be independent of each other. Do not restate the same violation in multiple criteria; only consider it in the most relevant criterion.

### Output Format
```json
{{
  "overall_analysis": "[Overall analysis]",
  "evaluation": {{
    "accuracy_and_depth": {{
      "comprehensive_evaluation": "[Analysis of accuracy and depth]",
      "score": [1-5]
    }},
    "logical_flow": {{
      "comprehensive_evaluation": "[Analysis of logical flow]",
      "score": [1-5]
    }}
  }}
}}
```

The transcript of the video is as follows:
{transcript}
"""

_fix_transcript = """You are an expert in YouTube video transcripts. There is a transcript that was automatically generated through YouTube, so it lacks proper capitalization and punctuation. Your task is to fix the transcript so that there is proper punctuation, capitalization, and spacing. Do not make other modifications (e.g., keep the original word choice).

You should enclose the fixed transcript with a <SCRIPT></SCRIPT> block, i.e.:
<SCRIPT>
(Fixed transcript here)
</SCRIPT>

Original transcript: {transcript}
"""

_image_eval = """# Task: Video Frame Quality Evaluation

You are tasked with analyzing and scoring a frame taken from a theorem explanation video. Note that you may not have the context of the video, so the captured frame may be a frame where some motion of visual elements is taking place. Your job is to assign a score from 1 to 5 for each criterion. Please provide a brief justification for your scores.

## Evaluation Criteria

1. **Visual Relevance**
   - Does the video frame align with the theorem's concepts and derivations?

2. **Element Layout**
   - Placemend and Size: Are the visual elements well-placed and appropriately sized within the frame?
   - Overlap: Are the visual elements free of unintentional overlap?
   - Clarity: Is the visual information conveyed in the frame clear and easy to understand?

## Scoring Instructions
1. Assign a score from **1 to 5** for each dimension:
   - **1**: Very poor quality, completely fails to meet the criteria.
   - **2**: Below average, significant issues present.
   - **3**: Acceptable, meets the basic criteria with minor issues.
   - **4**: Good, performs well with no major issues.
   - **5**: Excellent, fully meets or exceeds expectations.
2. Provide a comprehensive evaluation for each dimension.
3. Format your output in **JSON**

### JSON Output Format
```json
{{
  "overall_analysis": "[Provide a general assessment of the image's quality]",
  "evaluation": {{
    "visual_relevance": {{
      "comprehensive_evaluation": "[Analysis of visual relevance]",
      "score": [1-5]
    }},
    "element_layout": {{
      "comprehensive_evaluation": "[Analysis of element layout]",
      "score": [1-5]
    }}
  }}
}}
```

Description of the theorem:
{description}

Image:"""

