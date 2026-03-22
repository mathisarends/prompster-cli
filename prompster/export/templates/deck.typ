#let songs = json.decode(sys.inputs.at("songs"))

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
  fill: rgb("#0a0a0a"),
)

#set text(font: "New Computer Modern")

#set square(stroke: none)

// ── color palette for card backs ──
#let card_colors = (
  rgb("#e91e63"),  // pink
  rgb("#00bcd4"),  // cyan
  rgb("#4caf50"),  // green
  rgb("#ff9800"),  // orange
  rgb("#9c27b0"),  // purple
  rgb("#ffeb3b"),  // yellow
  rgb("#2196f3"),  // blue
  rgb("#ef5350"),  // red
  rgb("#26a69a"),  // teal
  rgb("#ab47bc"),  // violet
)

// deterministic color pick based on song index
#let pick_color(i) = {
  card_colors.at(calc.rem(i * 7 + 3, card_colors.len()))
}

// ── front side: QR with vinyl rings ──
#let qr_front_side(song) = {
  square(
    size: card_size,
    fill: rgb("#0d0d0d"),
  )[
    // concentric rings (vinyl/speaker look)
    #for r in range(12, 0, step: -1) {
      let ring_r = (r / 12) * 0.48 * card_size
      let alpha = if calc.rem(r, 2) == 0 { 85% } else { 92% }
      place(
        center + horizon,
        circle(
          radius: ring_r,
          stroke: 1.2pt + rgb("#e040fb").transparentize(alpha),
          fill: none,
        ),
      )
    }

    // outer ring accent
    #place(center + horizon)[
      #circle(
        radius: 0.48 * card_size,
        stroke: 0.6pt + rgb("#c724b1").transparentize(50%),
        fill: none,
      )
    ]

    // QR code center
    #align(center + horizon)[
      #rect(
        width: 55%,
        height: 55%,
        fill: white,
        radius: 2pt,
        stroke: 1.5pt + rgb("#c724b1"),
      )[
        #align(center + horizon)[
          #image(song.qr_file, width: 90%)
        ]
      ]
    ]

    // corner dots (subtle signature)
    #place(top + left, dx: 4pt, dy: 4pt)[
      #circle(radius: 1.5pt, fill: rgb("#e040fb").transparentize(40%))
    ]
    #place(top + right, dx: -7pt, dy: 4pt)[
      #circle(radius: 1.5pt, fill: rgb("#e040fb").transparentize(40%))
    ]
    #place(bottom + left, dx: 4pt, dy: -7pt)[
      #circle(radius: 1.5pt, fill: rgb("#e040fb").transparentize(40%))
    ]
    #place(bottom + right, dx: -7pt, dy: -7pt)[
      #circle(radius: 1.5pt, fill: rgb("#e040fb").transparentize(40%))
    ]
  ]
}

// ── back side: colorful card with black text ──
#let text_back_side(song, index) = {
  let bg = pick_color(index)

  square(
    size: card_size,
    fill: bg,
  )[
    // subtle inner border
    #place(top + left, dx: 3pt, dy: 3pt)[
      #rect(
        width: 100% - 6pt,
        height: 100% - 6pt,
        stroke: 1pt + black.transparentize(70%),
        fill: none,
        radius: 1pt,
      )
    ]

    #align(center + horizon)[
      #pad(left: 0.08 * card_size, right: 0.08 * card_size)[
        #stack(
          // artist
          block(
            height: 0.25 * card_size,
            width: 100%,
            align(
              center + horizon,
              text(
                fill: black,
                size: 0.06 * card_size,
                weight: "bold",
              )[#str(song.artist_names)]
            ),
          ),
          // divider
          block(
            width: 100%,
            align(center, rect(width: 50%, height: 1pt, fill: black.transparentize(50%))),
          ),
          // year
          block(
            height: 0.32 * card_size,
            width: 100%,
            align(
              center + horizon,
              text(
                fill: black,
                size: 0.28 * card_size,
                weight: "black",
              )[#str(song.release_year)]
            ),
          ),
          // divider
          block(
            width: 100%,
            align(center, rect(width: 50%, height: 1pt, fill: black.transparentize(50%))),
          ),
          // title
          block(
            height: 0.25 * card_size,
            width: 100%,
            align(
              center + horizon,
              text(
                fill: black,
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

  let idx = 0
  for page in songs.chunks(rows * cols) {
    let fronts = ()
    let backs = ()

    for song in page {
      fronts.push(qr_front_side(song))
      backs.push(text_back_side(song, idx))
      idx += 1
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
