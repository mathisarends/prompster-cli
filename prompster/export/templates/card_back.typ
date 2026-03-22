// card_back.typ — Hitster card back: year + title + artist
// Parameters injected via Typst CLI --input flags:
//   year        : release year string, e.g. "1994"
//   title       : track title
//   artist      : artist name(s)
//   card_index  : 1-based card number

#let year       = sys.inputs.at("year",       default: "????")
#let title      = sys.inputs.at("title",      default: "Unknown Title")
#let artist     = sys.inputs.at("artist",     default: "Unknown Artist")
#let card_index = sys.inputs.at("card_index", default: "?")

#set page(
  width:  6.3cm,
  height: 8.8cm,
  margin: 0pt,
)
#set text(font: "Liberation Sans", fallback: true)

// Dark background
#rect(
  width:  100%,
  height: 100%,
  fill:   rgb("#0d0d1a"),
)[
  // Neon border
  #rect(
    width:  100%,
    height: 100%,
    stroke: 2pt + rgb("#c724b1"),
    fill:   none,
  )

  // Top: artist name
  #align(center + top)[
    #pad(top: 12pt, left: 6pt, right: 6pt)[
      #text(
        fill:   white,
        size:   8pt,
        weight: "bold",
      )[#artist]
    ]
  ]

  // Center: big year
  #align(center + horizon)[
    #stack(
      spacing: 4pt,
      // "HITSTER DATA" label
      text(
        fill:    rgb("#c724b1"),
        size:    6pt,
        weight:  "bold",
        tracking: 3pt,
      )[HITSTER DATA],
      // The year itself
      text(
        fill:   rgb("#e040fb"),
        size:   52pt,
        weight: "bold",
      )[#year],
      // Decorative neon line
      rect(width: 60%, height: 2pt, fill: rgb("#c724b1")),
      // Track title
      pad(top: 4pt)[
        text(
          fill:   rgb("#ccccdd"),
          size:   7pt,
          style:  "italic",
        )[#title]
      ],
    )
  ]

  // Bottom: card index + branding
  #align(center + bottom)[
    #pad(bottom: 8pt)[
      #text(fill: rgb("#333355"), size: 5pt, tracking: 2pt)[
        [#card_index] POWERED BY GPT-4O-MINI
      ]
    ]
  ]
]
