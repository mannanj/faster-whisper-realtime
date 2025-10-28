# Task 10: Redesign UI to Match sun-taupe.vercel.app Design

- [x] Download and integrate Geist and Geist Mono fonts locally
- [x] Update HTML structure to match minimalist card-based layout
- [x] Implement clean typography with light font weights (300-400)
- [x] Apply clean white background with subtle borders
- [x] Style record button to match minimalist aesthetic
- [x] Update color scheme to neutral black/white palette
- [x] Add proper spacing and padding following reference design
- [x] Ensure monospace font for technical elements (duration, status)
- **Location:** `index.html`, new directory `static/fonts/`

## Design Reference

Site: https://sun-taupe.vercel.app

### Key Design Elements

**Typography:**
- Primary Font: Geist (system-ui fallback)
  - Headings: 24px, font-weight 300
  - Body: 16px
- Monospace Font: Geist Mono (SF Mono fallback)
  - Used for technical data, timestamps

**Layout:**
- Clean white background (rgb(255, 255, 255))
- Content in bordered card containers
- Generous padding and whitespace
- Centered, constrained-width layout
- Subtle 1-2px black borders

**Color Palette:**
- Background: White (#ffffff)
- Text: Black (#000000)
- Borders: Black (#000000), thin (1-2px)
- Accents: Minimal, primarily through borders and typography

**UI Elements:**
- Minimalist buttons with no background
- Clean, borderless inputs
- Card-based content sections with borders
- Icon + text combinations for headers
- Status indicators in corners (e.g., "DST ON" badge)

**Aesthetic:**
- Swiss/International Style influence
- Maximum clarity and readability
- No gradients or shadows
- Functional minimalism
- Monospace for data, sans-serif for content

### Implementation Notes

1. **Font Download:**
   - Download Geist font from https://vercel.com/font
   - Download Geist Mono from same source
   - Store in `static/fonts/` directory
   - Use @font-face declarations in CSS

2. **Layout Changes:**
   - Remove gradient backgrounds
   - Add bordered card container for main transcription area
   - Implement cleaner header with icon
   - Reduce visual noise from recording states

3. **Typography Hierarchy:**
   - Use lighter font weights (300 for headings)
   - Increase letter spacing subtly
   - Ensure proper line heights for readability
   - Monospace for duration, status, technical info

4. **Recording Button:**
   - Simplify to minimal border design
   - Remove heavy shadows and gradients
   - Clean state transitions
   - Possible circle with border approach

5. **Responsive Considerations:**
   - Maintain mobile-friendly touch targets
   - Ensure readability at all sizes
   - Keep clean borders visible on all screens
