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
  margin: (x: margin_x, y: margin_y)
)

#set text(font: "New Computer Modern")

#set square(stroke: none)

#let qr_front_side(song) = {
  square(
    size: card_size,
    inset: 0.5cm,
    image(song.qr_file, width: 100%)
  )
}

#let text_back_side(song) = {
  square(
    size: card_size,
    inset: 0.05 * card_size,
    stack(
      block(
        height: 0.3 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            str(song.artist_names),
            size: 0.06 * card_size
          )
        )
      ),
      block(
        height: 0.35 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            weight: "black",
            str(song.release_year),
            size: 0.28 * card_size
          )
        )
      ),
      block(
        height: 0.35 * card_size,
        width: 100%,
        align(
          center + horizon,
          text(
            emph(song.title),
            size: 0.06 * card_size
          )
        )
      )
    )
  )
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
