#import "@preview/cetz:0.4.1": canvas, draw
#import draw: circle, content, line, on-layer

#let data = yaml("_llm_summarized_topics.yml")

#set page(width: auto, height: auto, margin: 8pt)
#set text(weight: "bold")

// Per-level style: 0 = root, 1 = topics, 2 = subtopics
#let NODE_STYLE = (
  "0": (text-size: 16pt, radius_multi: 9.0),
  "1": (text-size: 12pt, radius_multi: 8.0),
  "2": (text-size: 12pt, radius_multi: 7.0),
)

// Layout params
#let r1 = 6               // topic stroke length
#let r2 = 4.75            // subtopic stroke length
#let sub-step = 40deg     // children step
#let start-angle = 0deg   // root "clockwise from=0"

// auto angle step based on number of branches
#let angle-step = if data.branches.len() == 0 { 360deg } else { 360deg / data.branches.len() }

// Draw a node at a given position.
#let node(pos, txt, color: orange, text-color: white, level: "1", styles: NODE_STYLE) = {
  let st = styles.at(level)
  let text-size = st.text-size
  let width = text-size * st.radius_multi

  // centered, wrapped label
  content(
    pos,
    frame: "circle",
    fill: color,
    stroke: .25pt + black,
    align(center, box(
      width: width,
      text(fill: text-color, size: text-size, hyphenate: false, txt),
    )),
  )
}

#let connect(a, b, stroke-color) = on-layer(-1, line(a, b, stroke: 3pt + stroke-color))

// Draw
#canvas({
  let center = (0, 0)

  // root
  node(
    center,
    [*#data.title*],
    color: orange,
    text-color: white, // root still fixed, or you can also add text_color in YAML
    level: "0",
  )

  // topics
  for (topic_idx, branch) in data.branches.enumerate() {
    let ang = start-angle - topic_idx * angle-step
    let parent-col = rgb(branch.color)
    let parent-text-col = rgb(branch.text_color) // from YAML
    let sub-start = (if branch.start_angle_deg == none { 45 } else { branch.start_angle_deg }) * 1deg

    let pos = (calc.cos(ang) * r1, calc.sin(ang) * r1)
    node(pos, branch.title, color: parent-col, text-color: parent-text-col, level: "1")
    connect(center, pos, parent-col)

    // evenly distribute children around the branch angle
    let num_children = branch.children.len()
    let spread = sub-step * (num_children - 1)
    for (child_idx, child) in branch.children.enumerate() {
      let offset = -spread / 2 + child_idx * sub-step
      let sub-ang = ang + offset
      let sub-pos = (
        pos.at(0) + calc.cos(sub-ang) * r2,
        pos.at(1) + calc.sin(sub-ang) * r2,
      )
      let child-col = rgb(child.color)
      let child-text-col = rgb(child.text_color) // from YAML
      node(sub-pos, child.title, color: child-col, text-color: child-text-col, level: "2")
      connect(pos, sub-pos, child-col)
    }
  }
})

#v(5pt)
#align(center, box(
  width: 12cm,
  height: auto,
  [#canvas({
    let (cbar_width, cbar_height) = (16cm, 0.8cm)

    // Color bar rectangle
    content(
      (0, 0),
      frame: "rect",
      fill: gradient.linear(..color.map.viridis),
      stroke: 0.5pt + rgb("#222222"),
      align(center, box(width: cbar_width, height: cbar_height)),
    )

    // Ticks and labels (log scale: 1, 10, 100, 1000)
    let tick_labels = ("1", "10", "100", "1000")
    let num_ticks = tick_labels.len() - 1
    for (tick_idx, tick_label) in tick_labels.enumerate() {
      let tick_x = -cbar_width / 2 + (cbar_width * tick_idx / num_ticks)
      line((tick_x, -0.2cm), (tick_x, -0.4cm), stroke: 1pt)
      content((tick_x, -0.75cm), align(center, text(size: 14pt, tick_label)))
    }
    // Axis label
    content((0, -1.5cm), align(center, text(size: 14pt, [Citation Counts (log)])))
  })],
))
