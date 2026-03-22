#let year       = sys.inputs.at("year",       default: "????")
#let title      = sys.inputs.at("title",      default: "Unknown Title")
#let artist     = sys.inputs.at("artist",     default: "Unknown Artist")

#set page(width: 6.3cm, height: 8.8cm, margin: 0pt)

#rect(width: 100%, height: 100%, fill: rgb("#0d0d1a"))[
  #rect(width: 100%, height: 100%, stroke: 2pt + rgb("#c724b1"), fill: none)

  #align(center + top)[
    #pad(top: 12pt, left: 6pt, right: 6pt)[
      #text(fill: white, size: 8pt, weight: "bold")[#artist]
    ]
  ]

  #align(center + horizon)[
    #stack(
      spacing: 4pt,
      text(fill: rgb("#c724b1"), size: 6pt, weight: "bold", tracking: 3pt)[HITSTER DATA],
      text(fill: rgb("#e040fb"), size: 52pt, weight: "bold")[#year],
      rect(width: 60%, height: 2pt, fill: rgb("#c724b1")),
      pad(top: 4pt)[
        #text(fill: rgb(204, 204, 221), size: 7pt, style: "italic")[#title]
      ],
    )
  ]
]
