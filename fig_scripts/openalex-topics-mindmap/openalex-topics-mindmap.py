# %% [markdown]
# Retrieve [research topics from OpenAlex](https://openalex.org/works?page=1&filter=cites%3Aw2015197254) for all works that cite the original pymatgen paper.
#
# Then use LLM to organize topics into a mindmap.
#
# Note:
# - You would need to get `OPENAI_API_KEY` to use OpenAI API, see https://openai.com/api/.

# /// script
# dependencies = ["requests", "openai", "pyyaml", "pymatviz", "plotly"]
# ///


import re
import subprocess
from collections import Counter

import plotly.colors
import requests
import yaml
from openai import OpenAI
from pymatviz.utils.plotting import pick_max_contrast_color

# %%
NUM_OF_MAIN_TOPICS: int = 5
NUM_OF_SUB_TOPICS: int = 4

# %% Step 1: Get topics from OpenAlex for 1st pymatgen paper


params = {"filter": "cites:w2015197254", "group_by": "primary_topic.id", "per_page": 50}
response = requests.get(
    "https://api.openalex.org/works", params=params, timeout=10
).json()

topic_counter = Counter(
    {
        group.get("key_display_name", "None"): group["count"]
        for group in response.get("group_by")
        if group["count"] >= 10  # Count for top 50 topics is around 10
    }
)

print("Topics from OpenAlex:")
for topic, count in topic_counter.items():
    print(f"  {topic:<60}{count}")

# %% Step 2: Use LLM to group topics


client = OpenAI()  # https://platform.openai.com/docs/overview

topic_list = "\n".join(f"- {topic} ({count})" for topic, count in topic_counter.items())

prompt = f"""
The following research topics are from papers that cite pymatgen, with each number indicating the count of citing works in that area.

Please organize them into {NUM_OF_MAIN_TOPICS} thematic branches that represent broader areas of materials research (e.g., batteries, machine learning, catalysis, ...), for each (sub)topic try to be as concise as possible (ideally within 5 words). Also please avoid duplicates (or very similar) (sub)topics.

Return output in a plain text tree structure (with indentation) without any header or metadata, e.g.:
    Topic_0:
        subtopic_0 (count_0)
        subtopic_1 (count_1)

    Topic_1:
        subtopic_0 (count_0)

Topics to work on today:
    {topic_list}
"""

chat_response = client.responses.create(
    model="gpt-5",  # WARNING: very slow
    input=prompt,
)

# print(chat_response.output_text)


def parse_mindmap(text: str) -> dict[str, list[tuple[str, int]]]:
    """
    Parse LLM response to machine-readable dict for plotter.
    """
    mindmap: dict[str, list[tuple[str, int]]] = {}
    current_topic = None

    for line in text.strip().splitlines():
        line = line.rstrip()

        if not line.strip():
            continue

        if not line.startswith(" "):  # Top-level topic
            current_topic = line.strip().removesuffix(":")
            mindmap[current_topic] = []

        elif current_topic:
            subtopic_line = line.strip()

            # Extract the (name, count)
            if match := re.match(r"^(.*)\s+\((\d+)\)$", subtopic_line):
                name = match[1].strip()
                count = int(match[2])
                mindmap[current_topic].append((name, count))
            else:
                raise ValueError(f"Cannot extract info from {subtopic_line=}")

    return mindmap


mindmap_dict: dict[str, list[tuple[str, int]]] = parse_mindmap(
    chat_response.output_text
)

# Sort main topics by the sum of subtopic counts
sorted_main_topics = sorted(
    mindmap_dict.items(),
    key=lambda item: sum(count for _, count in item[1]),
    reverse=True,
)

# Limit max number of main/sub topics
mindmap_dict = {
    main_topic: sorted(subtopics, key=lambda x: x[1], reverse=True)[:NUM_OF_SUB_TOPICS]
    for main_topic, subtopics in sorted_main_topics[:NUM_OF_MAIN_TOPICS]
}

for main_topic, subtopics in mindmap_dict.items():
    print(f"{main_topic} (total {sum(c for _, c in subtopics)}):")
    for name, count in subtopics:
        print(f"    - {name} ({count})")

# %% Step 3: Export LLM summarized topic data to YAML for Typst

START_ANGLES = [45, 10, -60, 200, 120]
assert len(START_ANGLES) == NUM_OF_MAIN_TOPICS

# Preserve current sorted/truncated order from Step 2
ordered_main = list(mindmap_dict.items())
if len(ordered_main) != NUM_OF_MAIN_TOPICS:
    raise ValueError(f"Unexpected number of topics, expect {NUM_OF_MAIN_TOPICS}")

# --- Collect all child values for global min/max ---
all_values = [count for _, subs in ordered_main for _, count in subs]
vmin, vmax = min(all_values), max(all_values)

# --- Choose colormap & normalizer ---
# Use viridis-like colors for consistency with Typst colorbar
viridis_colors = ["#440154", "#31688e", "#1f9e89", "#35b779", "#b0dd2f", "#fde725"]


def value_to_hex(val: float) -> str:
    """Map a numeric value to a hex color using Plotly's sample_colorscale."""
    # Normalize value to [0, 1] range
    normalized = (val - vmin) / (vmax - vmin)
    # Sample the colorscale at the normalized position
    color = plotly.colors.sample_colorscale(
        viridis_colors, normalized, colortype="hex"
    )[0]
    return color


def with_text_color(hex_color: str) -> tuple[str, str]:
    """Return (fill_color_hex, text_color_hex) with max contrast, both in hex."""
    text_col = pick_max_contrast_color(hex_color)
    text_hex = text_col.hex
    return hex_color, text_hex


# --- Build YAML data ---
branches = []
for i, (main_title, subtopics) in enumerate(ordered_main):
    children = []
    for sub_title, count in subtopics:
        fill, text_col = with_text_color(value_to_hex(count))
        children.append(
            {
                "title": sub_title,
                "value": int(count),
                "color": fill,
                "text_color": text_col,
            }
        )
    # Parent color from sum of children
    parent_val = sum(c["value"] for c in children)
    parent_fill, parent_text = with_text_color(value_to_hex(parent_val))
    branches.append(
        {
            # remove topic_x header (LLM sometimes ignore this request)
            "title": main_title.split(":", maxsplit=2)[1].strip(),
            "color": parent_fill,
            "text_color": parent_text,
            "start_angle_deg": START_ANGLES[i],
            "children": children,
        }
    )

data = {"title": "pymatgen", "branches": branches}

with open("_llm_summarized_topics.yml", "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

# %% Step 4: Compile Typst to SVG
subprocess.run(["typst", "compile", "mindmap.typ", "../../paper/figs/mindmap.pdf"])
