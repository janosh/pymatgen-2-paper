#import "@preview/cetz:0.4.1": canvas, draw
#import draw: circle, content, line, on-layer

#let data = yaml("_llm_summarized_topics.yml")

#set page(width: auto, height: auto, margin: 8pt)
#set text(weight: "bold")

// Per-level style: 0 = root, 1 = topics, 2 = subtopics
#let NODE_STYLE = (
  "0": (text-size: 14pt, radius_multi: 9.0),
  "1": (text-size: 9pt, radius_multi: 8.0),
  "2": (text-size: 7pt, radius_multi: 7.0),
)

// Layout params
#let r1 = 4               // topic stroke length
#let r2 = 3               // subtopic stroke length
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
  for (i, b) in data.branches.enumerate() {
    let ang = start-angle - i * angle-step
    let parent-col = rgb(b.color)
    let parent-text-col = rgb(b.text_color) // from YAML
    let sub-start = (if b.start_angle_deg == none { 45 } else { b.start_angle_deg }) * 1deg

    let pos = (calc.cos(ang) * r1, calc.sin(ang) * r1)
    node(pos, b.title, color: parent-col, text-color: parent-text-col, level: "1")
    connect(center, pos, parent-col)

    // evenly distribute children around the branch angle
    let n_children = b.children.len()
    let spread = sub-step * (n_children - 1)
    for (j, child) in b.children.enumerate() {
      let offset = -spread / 2 + j * sub-step
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

// Load colorbar
#v(5pt)
#align(center, box(
  width: 12cm,
  height: auto,
  [#canvas({
    let (cbar_width, cbar_height) = (12cm, 0.4cm)

    // Color bar rectangle
    content(
      (0, 0),
      frame: "rect",
      fill: gradient.linear(..color.map.viridis),
      stroke: 0.5pt + rgb("#222222"),
      align(center, box(width: cbar_width, height: cbar_height)),
    )

    // Ticks and labels (log scale: 1, 10, 100, 1000)
    let ticks = ("1", "10", "100", "1000")
    let n = ticks.len() - 1
    for (i, t) in ticks.enumerate() {
      let x = -cbar_width / 2 + (cbar_width * i / n)
      line((x, -0.15cm), (x, -0.25cm), stroke: 0.7pt)
      content((x, -0.45cm), align(center, text(size: 7pt, t)))
    }
    // Axis label
    content((0, -0.9cm), align(center, text(size: 8pt, [Citation Counts (log)])))
  })],
))
