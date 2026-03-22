#let songs = json("songs.json")

#let page_width = 210mm
#let page_height = 297mm
#let margin_x = 2cm
#let margin_y = 1cm

#let rows = 5
#let cols = 3
#let card_size = 5cm

#let marking_padding = 1cm

#set page(
  width: page_width,
  height: page_height,
  margin: (x: margin_x, y: margin_y),
  fill: rgb("#06060e"),
)

#set text(font: "New Computer Modern")

#set square(stroke: none)

// ── color palette ──
#let bg_deep    = rgb("#06060e")
#let bg_scan    = rgb("#0a0a18")
#let neon_pink  = rgb("#c724b1")
#let neon_light = rgb("#e040fb")
#let text_light = rgb("#ccccdd")

// ── shared: cyberpunk card base with scanlines, double border, corner accents ──
#let cyber_card(body) = {
  square(
    size: card_size,
    fill: bg_deep,
  )[
    // scanlines
    #place(top + left)[
      #for i in range(25) {
        place(
          top + left,
          dy: i * 0.2cm,
          rect(
            width: 100%,
            height: 0.08cm,
            fill: if calc.rem(i, 2) == 0 { bg_scan } else { bg_deep },
          ),
        )
      }
    ]

    // outer glow border
    #place(top + left, dx: 2pt, dy: 2pt)[
      #rect(
        width: 100% - 4pt,
        height: 100% - 4pt,
        stroke: 0.7pt + neon_light.transparentize(60%),
        fill: none,
        radius: 1.5pt,
      )
    ]

    // inner neon border
    #place(top + left, dx: 5pt, dy: 5pt)[
      #rect(
        width: 100% - 10pt,
        height: 100% - 10pt,
        stroke: 1.5pt + neon_pink,
        fill: none,
        radius: 1pt,
      )
    ]

    // corner accents
    #place(top + left, dx: 3pt, dy: 3pt)[
      #rect(width: 4pt, height: 4pt, fill: neon_light)
    ]
    #place(top + right, dx: -7pt, dy: 3pt)[
      #rect(width: 4pt, height: 4pt, fill: neon_light)
    ]
    #place(bottom + left, dx: 3pt, dy: -7pt)[
      #rect(width: 4pt, height: 4pt, fill: neon_light)
    ]
    #place(bottom + right, dx: -7pt, dy: -7pt)[
      #rect(width: 4pt, height: 4pt, fill: neon_light)
    ]

    #body
  ]
}

// ── front side: QR code ──
#let qr_front_side(song) = {
  cyber_card()[
    #align(center + horizon)[
      #box()[
        #place(center + horizon)[
          #rect(
            width: 80% + 6pt,
            height: 80% + 6pt,
            fill: neon_pink.transparentize(88%),
            radius: 2pt,
          )
        ]
        #rect(
          width: 80%,
          height: 80%,
          stroke: 1.2pt + neon_pink,
          fill: white,
          radius: 1.5pt,
        )[
          #align(center + horizon)[
            #image(song.qr_file, width: 90%)
          ]
        ]
      ]
    ]
  ]
}

// ── back side: artist / year / title ──
#let text_back_side(song) = {
  cyber_card()[
    #align(center + horizon)[
      #pad(left: 0.05 * card_size, right: 0.05 * card_size)[
        #stack(
          // artist
          block(
            height: 0.25 * card_size,
            width: 100%,
            align(
              center + horizon,
              text(
                fill: white,
                size: 0.06 * card_size,
                weight: "bold",
              )[#str(song.artist_names)]
            ),
          ),
          // divider
          block(
            width: 100%,
            align(center, rect(width: 60%, height: 0.8pt, fill: neon_pink)),
          ),
          // year
          block(
            height: 0.30 * card_size,
            width: 100%,
            align(
              center + horizon,
              box()[
                #place(center + horizon)[
                  #text(
                    fill: neon_light.transparentize(80%),
                    size: 0.30 * card_size,
                    weight: "black",
                  )[#str(song.release_year)]
                ]
                #text(
                  fill: neon_light,
                  size: 0.28 * card_size,
                  weight: "black",
                )[#str(song.release_year)]
              ]
            ),
          ),
          // divider
          block(
            width: 100%,
            align(center, stack(
              spacing: 1pt,
              rect(width: 50%, height: 1.5pt, fill: neon_pink),
              rect(width: 50%, height: 0.4pt, fill: neon_light.transparentize(50%)),
            )),
          ),
          // title
          block(
            height: 0.25 * card_size,
            width: 100%,
            align(
              center + horizon,
              text(
                fill: text_light,
                size: 0.06 * card_size,
                style: "italic",
              )[#song.title]
            ),
          ),
        )
      ]
    ]
  ]
}

#let marking_line = line(
  stroke: (paint: gray, thickness: 0.5pt),
  length: marking_padding / 2
)

#let marking(angle) = {
  rotate(
    angle,
    reflow: true,
    box(
      width: marking_padding,
      height: card_size,
      stack(
        spacing: card_size,
        ..(marking_line,) * 2
      )
    )
  )
}

#let marking_row(angle) = {
  (
    square(size: marking_padding),
    ..(marking(angle),) * cols,
    square(size: marking_padding),
  )
}

#let pad_page(page) = {
  let page_rows = page.chunks(cols)
  let padded_rows = page_rows.map(
    row => (marking(0deg), ..row, marking(180deg))
  )
  return (
    ..marking_row(90deg),
    ..padded_rows.flatten(),
    ..marking_row(270deg)
  )
}

#let get_pages(songs) = {
  let pages = ()

  for page in songs.chunks(rows * cols) {
    let fronts = ()
    let backs = ()

    for song in page {
      fronts.push(qr_front_side(song))
      backs.push(text_back_side(song))
    }

    for _ in range(rows * cols - page.len()) {
      fronts.push(square(size: card_size))
      backs.push(square(size: card_size))
    }

    let reversed_backs = backs.chunks(cols).map(row => row.rev()).flatten()

    pages.push(pad_page(fronts))
    pages.push(pad_page(reversed_backs))
  }

  return pages
}

#for (i, page) in get_pages(songs).enumerate() {
  if i != 0 { pagebreak() }
  grid(
    columns: cols + 2,
    ..page
  )
}
