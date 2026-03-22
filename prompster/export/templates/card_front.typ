#let qr_path    = sys.inputs.at("qr_path",    default: "")
#let card_index = sys.inputs.at("card_index", default: "?")

#set page(width: 6.3cm, height: 8.8cm, margin: 0pt)

#rect(width: 100%, height: 100%, fill: rgb("#0d0d1a"))[
  #rect(width: 100%, height: 100%, stroke: 2pt + rgb("#c724b1"), fill: none)

  #align(center + top)[
    #pad(top: 10pt)[
      #text(fill: rgb("#c724b1"), size: 6pt, weight: "bold", tracking: 3pt)[HITSTER]
    ]
  ]

  #align(center + horizon)[
    #if qr_path != "" {
      image(qr_path, width: 72%)
    } else {
      rect(width: 72%, height: 72%, fill: rgb("#1a1a2e"), stroke: 1pt + rgb("#c724b1"))
    }
  ]

  #align(center + bottom)[
    #pad(bottom: 8pt)[
      #text(fill: rgb("#555577"), size: 6pt)[#card_index]
    ]
  ]
]
