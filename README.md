# Family Cookbook: Paul & Nino Wagner

A curated collection of recipes from our family; a gift meant to survive us for our children and theirs. This cookbook preserves traditional recipes from Georgian, Russian, Ukrainian, and Armenian culinary traditions (reflecting the Wagner, Akinian, and Diasamidze families), alongside modern recipes we've gathered from various sources since we got married.

## Purpose

This cookbook is a living archive of family recipes and favorites, meant to be:
- **Preserved for future generations** - A lasting gift for our children and beyond
- **Shared with community** - Friends in Georgian/Russian/Ukrainian/Armenian communities are welcome to fork this repository and add their own family recipes
- **A growing collection** - Includes both traditional family recipes and recipes we've discovered together from online sources

## Recipe Sources

- **Family Traditions** - Recipes from the Wagner, Akinian, and Diasamidze families, primarily in Georgian, Russian, Ukrainian, and Armenian
- **Modern Favorites** - Recipes we've collected from various web sources since our marriage, primarily in English
- **Community Contributions** - Friends are encouraged to fork and contribute their own family recipes

## Project Structure

### Directory Organization

- **`artifacts/`** - Raw scans/photos
  - `artifacts/english/` - Raw English recipe scans (`.jpeg`)
  - `artifacts/georgian/` - Raw Georgian recipe scans (`.jpeg`)
  
- **`assets/`** - Processed images ready for use
  - `assets/english/` - Treated English recipe images (background removed, cropped) (`.png`)
  - `assets/georgian/` - Treated Georgian recipe images (background removed, cropped) (`.png`)

### File Naming Convention

Each image should have a **companion Markdown file** with the same name:

- `IMG_1161.png` → `IMG_1161.md`
- `IMG_1162.png` → `IMG_1162.md`

The Markdown files contain:
- **English translation** with recipe formatting
- Historical and cultural context (for traditional recipes)
- Original text in the source language(s)
- Ingredients, instructions, and notes

## Workflow

### 1. Image Processing Pipeline

1. **Raw Scans** → Start with photos/scans in `artifacts/`
2. **Image Treatment** → Process images (background removal, crop empty space)
3. **Save to Assets** → Move treated images to `assets/`
4. **Create Companion MD** → Generate or update the corresponding `.md` file

### 2. Translation Workflow

For creating English translations and condensed recipe versions, use the **Culinary Translator & Recipe Historian** web application:

🔗 **https://culinary-translator-recipe-historian-815460826928.us-west1.run.app/**

#### Using the Culinary Translator:

1. Open the web application
2. Upload or input the recipe text (original language)
3. The app will generate:
   - Contextual English translation
   - Recipe formatting (Ingredients, Instructions, Notes)
   - Historical/cultural context where relevant
   - Condensed version suitable for recipe book publication

4. Copy the generated content into the companion `.md` file
5. Include the original text at the bottom for reference

### 3. Markdown File Format

Each `.md` file should follow this structure:

```markdown
# Recipe Title

Brief contextual description with historical or cultural notes.

## Ingredients
> * Ingredient 1
> * Ingredient 2
> ...

## Instructions
> 1. Step one
> 2. Step two
> ...

## Notes
* **Important note:** Details
* **Tip:** Helpful information

### Original [Language] Text
[Original text preserved for reference]
```

## Card resolution

The scan cards on each verso are baked once into `print/cards/` by
`scripts/make_cards.py` and then embedded in the PDF. They are the bulk of the
file, so their resolution sets how big the book is.

`CARD_MAX_DIM` caps the long side of a baked card in pixels. The default is
1800, which is full quality. Lower it only when something forces you to, and the
only thing that realistically does is a print service's upload limit (Lulu caps
uploads at 500 MB; others sit between 1 and 2 GB).

Measured on this book, 201 pages:

| CARD_MAX_DIM | dpi on the page | cards | whole PDF | what you lose |
|---|---|---|---|---|
| 1800 (default) | 286 | 390 MB | 515 MB | nothing |
| 1400 | 222 | 271 MB | 401 MB | graph-paper grid softens slightly |
| 1200 | 190 | ~168 MB | ~300 MB | grid goes mushy; handwriting still legible |
| 1000 | 158 | ~117 MB | ~250 MB | visibly soft, fine for a markup dummy |

The dpi figure is for a card printed at the full 330pt width. Cards scaled up
per-recipe (`scale:` in frontmatter) land proportionally lower, so a card at
`scale: 1.3` is around 220 dpi even at the 1800 default.

Handwriting stays readable at every setting in that table. The detail that goes
first is the pale graph-paper grid on Zeinab's notebook pages, which is part of
what makes the cards read as her notebook rather than as anonymous paper.

To build small, set the variable for the bake and then compile as usual:

```bash
CARD_MAX_DIM=1000 python3 scripts/make_cards.py
typst compile --root . --font-path assets/fonts print/cookbook.typ print/cookbook.pdf
```

To go back to full quality, bake again without the variable:

```bash
python3 scripts/make_cards.py
```

The cache records the size it was baked at and wipes itself whenever that
changes, so a book can never end up half one resolution and half another. A full
rebake of all cards takes two or three minutes.

## Typesetting: title line breaks

Recipe titles are set large on the verso page, in a column that fits only a few
words per line. Two things control how a title breaks.

**Automatic:** the build glues the last two words of a title together when the
final word is short (10 characters or fewer), so a title never ends with a lone
stubby word on its own line. Body text gets the same treatment at 7 characters.
Nothing to do; this just happens.

**Manual:** put `|` in the title where you want a line to break. The `|` is
print-only. The table of contents, the index, the printed footer slug, and the
website all get the clean title with the bars stripped out.

Reach for `|` when the automatic break looks wrong. Real example, the
chilaquiles casserole in `assets/georgian/1200/IMG_1200.md`. Written plainly,
the automatic rule bound "Chilaquiles Casserole" and stranded a single word:

```
New Seasons Market
Cheesy
Chilaquiles Casserole
```

Written with explicit breaks:

```yaml
title: New Seasons Market|Cheesy Chilaquiles|Casserole
```

it sets as three balanced lines:

```
New Seasons Market
Cheesy Chilaquiles
Casserole
```

Check the result by proofing that one recipe rather than the whole book:

```
typst compile --root . --font-path assets/fonts --input only=<slug> \
  --format png --ppi 110 print/cookbook.typ 'proof-{p}.png'
```

The verso editor (`python3 scripts/verso_editor.py`, localhost:8766) has a
"Proof PDF pages" button that does the same thing in the browser.

## Examples

See existing recipe files:
- `assets/georgian/IMG_1161.md` - Dumpling Dough with Boiling Water
- `assets/georgian/IMG_1162.md` - Lyudmila's Beef Stroganoff

## Design Files

The project includes InDesign files for cookbook layout:
- `Minimalistic Cookbook A4.indd`
- `Minimalistic Cookbook A4.idml`
- `Minimalistic Cookbook A4.af` (Affinity Designer)

## Contributing

When adding new recipes:

1. ✅ Ensure raw scan is in `artifacts/` (if applicable)
2. ✅ Process image (background removal, cropping) → save to `assets/` (if applicable)
3. ✅ Create/update companion `.md` file with same name
4. ✅ Use [Culinary Translator](https://culinary-translator-recipe-historian-815460826928.us-west1.run.app/) for translations of traditional recipes
5. ✅ Preserve original text in the Markdown file (for traditional recipes)
6. ✅ Include cultural/historical context where relevant (for traditional recipes)
7. ✅ Credit original sources for modern recipes from web sources

### Forking for Your Own Family

Friends in the Georgian/Russian/Ukrainian/Armenian communities are welcome to:
- Fork this repository
- Add your own family recipes following the same structure
- Create your own version of the family cookbook
- Contribute back recipes that might be meaningful to share

## Notes

- All images are treated (background removal, cropped) before being added to `assets/`
- Companion `.md` files are essential for the recipe book workflow
- Original text should always be preserved in the Markdown files for traditional recipes
- The culinary translator app helps create publication-ready condensed versions
- This is a living archive—recipes continue to be added as we discover and preserve them