#import "@preview/cetz:0.4.1": canvas, draw
#import draw: circle, content, line, on-layer

#let data = yaml("llm_summarized_topics.yml")

#set page(width: auto, height: auto, margin: 8pt)
#set text(weight: "bold")

// -------- helpers --------
#let node(pos, txt, color: orange, text-color: white, size: 1.0) = {
  // draw the circle (radius is in canvas units)
  circle(pos, radius: size, fill: color, stroke: 2pt + white)

  // text size
  let tsize = if size >= 1.5 { 14pt } else if size >= 1.2 { 10pt } else { 8.5pt }

  // set a box width based on text size
  let w = tsize * 8.0  // TODO: need tweaking

  // center a constrained-width box at the same position; text will wrap
  content(
    pos,
    align(center, box(
      width: w,
      text(
        fill: text-color,
        size: tsize,
        hyphenate: true,
        lang: "en",
        align(center, txt),
      ),
    )),
  )
}

#let connect(a, b, stroke-color) = on-layer(-1, line(a, b, stroke: 3pt + stroke-color))

// -------- layout params --------
#let r1 = 3.8            // level-1 radius
#let r2 = 3.0            // level-2 radius
#let angle-step = 72deg  // 5 evenly spaced branches
#let sub-step = 45deg    // children step
#let start-angle = 0deg  // root "clockwise from=0"

// -------- draw --------
#canvas({
  // root
  let center = (0, 0)
  node(center, [*#data.title*], color: orange, text-color: white, size: 1.6)

  // place branches clockwise from 0°, children start at each branch's start_angle_deg (clockwise)
  for (i, b) in data.branches.enumerate() {
    let ang = start-angle - i * angle-step
    let col = rgb(b.color)                // hex like "#FFD700"
    let sub-start = (if b.start_angle_deg == none { 45 } else { b.start_angle_deg }) * 1deg

    let pos = (calc.cos(ang) * r1, calc.sin(ang) * r1)
    node(pos, b.title, color: col, text-color: black, size: 1.2)
    connect(center, pos, col)

    for (j, child) in b.children.enumerate() {
      let sub-ang = sub-start - j * sub-step
      let sub-pos = (pos.at(0) + calc.cos(sub-ang) * r2,
                     pos.at(1) + calc.sin(sub-ang) * r2)
      node(sub-pos, child.title, color: col, text-color: black, size: 0.85)
      connect(pos, sub-pos, col)
    }
  }
})
