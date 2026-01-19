# Recipe Collection

A curated collection of traditional recipes, primarily from Georgian and Russian culinary traditions, digitized and translated for preservation and accessibility.

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
- Historical and cultural context
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

1. ✅ Ensure raw scan is in `artifacts/`
2. ✅ Process image (background removal, cropping) → save to `assets/`
3. ✅ Create/update companion `.md` file with same name
4. ✅ Use [Culinary Translator](https://culinary-translator-recipe-historian-815460826928.us-west1.run.app/) for English translations
5. ✅ Preserve original text in the Markdown file
6. ✅ Include cultural/historical context where relevant

## Notes

- All images are treated (background removal, cropped) before being added to `assets/`
- Companion `.md` files are essential for the recipe book workflow
- Original text should always be preserved in the Markdown files for reference
- The culinary translator app helps create publication-ready condensed versions
