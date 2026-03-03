// Subfigure support
#let subfigure-kind = "subfigure"

// Immediate enclosing figure of a subfigure: the nearest preceding figure of
// any kind (image, table, ...) that is not itself a subfigure. Used to scope
// the `within` sibling lookup that determines the subfigure letter.
#let subfigure-parent(loc) = (
  query(selector(figure).before(loc)).filter(fig => fig.kind != subfigure-kind).last()
)

// 1-based letter index of a subfigure among the siblings sharing its parent
// figure, via the `within` selector (Typst 0.15) — no manually stepped counter
// that had to be reset by a show rule per parent. `inclusive: false` counts only
// strictly-preceding siblings, so this works both during layout (loc = here(),
// before the figure is emitted) and from ref rules (loc = the figure itself).
#let subfigure-index(loc) = (
  query(
    figure.where(kind: subfigure-kind).within(subfigure-parent(loc).location()).before(loc, inclusive: false),
  ).len() + 1
)

#let subfigure(
  body,
  pos: bottom + center,
  dx: 0%,
  dy: 6%,
  caption: "",
  numbering: "a)",
  label: none,
  supplement: none,
  placement: top,
) = {
  let fig = figure(
    body,
    caption: none,
    kind: subfigure-kind,
    supplement: none,
    numbering: numbering,
    outlined: false,
    placement: placement,
  )

  context {
    let sub-fig-num = std.numbering(numbering, subfigure-index(here()))
    return [ #fig#label #place(pos, dx: dx, dy: dy)[#supplement #sub-fig-num #caption] ]
  }
}

// Define a function to use the ORCID SVG logo with minimal padding
#let orcid-logo(height: 1em) = {
  box(height: height, image("figs/orcid-logo.svg"))
}

#let header-block(args) = block(
  text(weight: 200, 24pt, fill: white, args.header.article-type),
  fill: args.header.article-color,
  width: 100%,
  inset: 10pt,
  radius: 2pt,
)

#let header-journal(args) = {
  block(
    inset: 0.2cm,
    width: 100%,
    {
      text(28pt, args.at("venue", default: none))
      h(1fr)
      text(28pt, args.header.article-meta)
    },
  )
}

#let precis-dates(args) = {
  align(bottom)[
    #table(
      inset: 0pt,
      row-gutter: 0.15cm,
      stroke: none,
      columns: (1fr, 1fr),
      ..args
        .dates
        .map(entry => {
          return (
            text(size: 7pt, entry.type),
            text(size: 7pt, entry.date.display()),
          )
        })
        .flatten()
    )

    #if (args.doi != none) { text(size: 7pt, link("http://doi.org/" + args.doi, [DOI: #args.doi])) }
  ]
}

#let author(author, affiliations: none) = {
  text(author.name)
  if (author.corresponding == true) [#strong[\*]]
  // Handle affiliations
  if (author.at("affiliations", default: none) != none) {
    // Map affiliation keys to labels
    let aff_labels = ()

    if (affiliations != none) {
      for aff_key in author.affiliations {
        for aff in affiliations {
          if (aff.at("key", default: none) == aff_key) {
            aff_labels.push(aff.label)
          }
        }
      }
    }

    if (aff_labels.len() > 0) {
      super(text(size: 1.3em, aff_labels.join(",")))
    }
  }
  if (author.at("orcid", default: none) != none) {
    h(0.3em)
    link("https://orcid.org/" + author.orcid, orcid-logo(height: 0.9em))
  }
}

#let display-affiliations(affiliations) = {
  if affiliations != none {
    block(inset: (top: 0.3em))[
      #for aff in affiliations [
        #aff.label: #aff.affiliation #h(0.5em)
      ]
    ]
  }
}

#let precis-title-authors-abstract(args) = {
  block(text(size: 15pt, weight: 500, args.title))

  // Pass affiliations to the author function
  let affiliations = args.at("affiliations", default: none)
  let author_fn = author
  args.authors.map(auth => author_fn(auth, affiliations: affiliations)).join(", ", last: " and ")

  if affiliations != none {
    display-affiliations(affiliations)
  }

  v(1.618em, weak: true)

  for (title, content) in args.abstracts {
    if (args.abstracts.len() > 1) { block[*#title*] }
    content
  }
}

#let precis(args) = {
  pad(
    top: 0.3em,
    bottom: 0.3cm,
    x: 0em,
    grid(
      columns: (1.4fr, 5fr),
      gutter: 0em,
      precis-dates(args), precis-title-authors-abstract(args),
    ),
  )
}

#let footer-render(parity: false, args) = {
  let footer-internal-content = (
    context counter(page).display(),
    h(0.75em),
    [|],
    h(1em),
    text(size: 8pt, args.citation),
  )
  if not parity { footer-internal-content = footer-internal-content.rev() }
  align(if parity { left } else { right }, footer-internal-content.join())
}

#let odd-even-page(content-odd: [], content-even: []) = {
  locate(loc => if calc.even(loc.page()) { content-even } else { content-odd })
}

#let footer(args) = odd-even-page(
  content-odd: footer-render(parity: false, args),
  content-even: footer-render(parity: true, args),
)

#let float(
  content,
  align: bottom,
) = {
  place(
    align,
    float: true,
    box(width: 100%)[
      #if (align == bottom) {
        line(length: 100%, stroke: 0.5pt)
        v(0.6em)
      }
      #content
      #if (align == top) {
        v(0.6em)
        line(length: 100%, stroke: 0.5pt)
      }
    ],
  )
}

#let template(body, ..args) = {
  let named = args.named()

  // Handle aliases and ensure arrays
  let get-array(key, ..aliases) = {
    for alias in (key,) + aliases.pos() {
      if alias in named {
        return if type(named.at(alias)) == array { named.at(alias) } else { (named.at(alias),) }
      }
    }
    return ()
  }

  let header = named.at("header", default: (:))
  let args = (
    header: (
      article-type: header.at("article-type", default: "Article"),
      article-color: header.at("article-color", default: rgb(167, 195, 212)),
      article-meta: header.at("article-meta", default: []),
    ),
    title: named.at("title", default: none),
    subtitle: named.at("subtitle", default: none),
    short-title: named.at("short-title", default: named.at("running-title", default: named.at(
      "running-head",
      default: none,
    ))),
    authors: get-array("authors", "author").map(a => (
      name: a.name,
      corresponding: a.at("corresponding", default: false),
      orcid: a.at("orcid", default: none),
      affiliations: a.at("affiliations", default: none),
    )),
    affiliations: named.at("affiliations", default: named.at("affiliation", default: none)),
    abstracts: get-array("abstracts", "abstract").map(a => if type(a) == dictionary { a } else {
      (title: "Abstract", content: a)
    }),
    citation: named.at("citation", default: none),
    open-access: named.at("open-access", default: none),
    venue: named.at("venue", default: none),
    doi: named.at("doi", default: none),
    keywords: named.at("keywords", default: ()),
    dates: get-array("dates", "date").map(d => if type(d) == datetime { (type: none, date: d) } else {
      (type: d.at("type", default: none), date: d.date)
    }),
  )

  set text(lang: "en", size: 9pt)

  // Set up page with custom footer that handles odd/even pages using the context approach
  set page(
    footer: context {
      set text(size: 8pt)
      let page-number = counter(page).get().first()

      if calc.odd(page-number) {
        // Odd page - align left
        align(left)[
          #counter(page).display() #h(0.75em) | #h(1em) #args.citation
        ]
      } else {
        // Even page - align right
        align(right)[
          #args.citation #h(1em) | #h(0.75em) #counter(page).display()
        ]
      }
    },
  )

  show heading: set block(above: 1.4em, below: 0.8em)
  show heading: set text(size: 12pt)
  set heading(numbering: "1.1")
  set par(leading: 0.618em, justify: true)

  // Let long inline code wrap across lines via zero-width breaks after "." and "_"
  show std.raw.where(block: false): it => {
    show regex("[._]"): chr => chr + sym.zws
    it
  }

  v(1.2em)
  header-journal(args)
  header-block(args)
  precis(args)
  v(0.8em)

  // Main body
  set text(lang: "en", size: 9pt)
  set par(first-line-indent: 0.45cm)
  // Fix deprecated paragraph spacing syntax
  set par(spacing: 0.618em)
  show: columns.with(2, gutter: 1.618em)

  show figure.caption: c => {
    set par(justify: true, first-line-indent: 0cm)
    v(2em, weak: false) // gap between main caption and subfigure captions
    align(center, context {
      par(justify: true, first-line-indent: 0cm)[
        *#c.supplement #c.counter.display(c.numbering)#c.separator*#c.body
      ]
    })
    v(1em, weak: false) // gap between main caption main body
  }

  set math.equation(numbering: "(Eq. 1)")
  show math.equation: set block(spacing: 1em, above: 1.618em, below: 1em)

  // format references to subfigures as "Figure 1a)"
  show ref: itm => {
    let elem = itm.element
    if elem != none and elem.func() == figure and elem.kind == subfigure-kind {
      // Immediate enclosing figure (any kind) gives both the correct supplement
      // and number: "Figure N" for image parents, "Table N" for table parents.
      let parent = subfigure-parent(elem.location())
      let parent-num = counter(figure.where(kind: parent.kind)).at(parent.location()).first()
      let subfig-num = numbering(elem.numbering, subfigure-index(elem.location()))
      return [#parent.supplement #parent-num#subfig-num]
    }
    itm
  }

  body
}
