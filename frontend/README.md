# Journal AI - AI-Powered Journaling Application

An elegant journaling application with voice transcription, AI assistance, and a beautiful calendar interface.

**Author:** Haider Amin

## Features

- 📅 **Visual Calendar** - Year-at-a-glance view with all 12 months
- 🎤 **Voice Journaling** - Record entries using voice with AI transcription
- ✍️ **Text Editor** - Clean document-style interface for writing
- ⭐ **Entry Management** - Star, hide, and manage your journal entries
- 🎨 **Beautiful UI** - Dark blue to purple gradient theme with elegant typography
- 📊 **Entry Tracking** - Visual indicators showing journaling progress
- 🔒 **Smart Date Control** - Future dates are disabled (can't journal before the day happens!)

## Tech Stack

- **React** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Styling with modern utility classes
- **Inter Font** - Professional, elegant typography

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (comes with Node.js)

### Installation

1. Clone or navigate to the project directory:
```bash
cd /home/haider-amin/projects/tailwind
```

2. Install dependencies (if not already installed):
```bash
npm install
```

### Running the Application

Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:5173/`

### Building for Production

To create a production build:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Application Structure

### Pages

1. **Landing Page** (`Landing.jsx`)
   - Marketing homepage with features, testimonials, and pricing
   - Login button to access the app

2. **Calendar View** (`Calendar.jsx`)
   - Year calendar with all 12 months visible
   - Click days to view/create entries
   - Entry management sidebar

3. **AI Talk Page** (`AITalk.jsx`)
   - Document-style text editor
   - Voice recording controls
   - AI assistant interface

### Components

- **ProfileMenu** (`ProfileMenu.jsx`) - User profile dropdown with settings and logout
- **App** (`App.jsx`) - Main application router and state management

## Usage

### Creating an Entry

1. Click the **Login** button on the landing page (auto-logs you in)
2. Click any **past or current date** on the calendar (future dates are disabled)
3. Click **Create Entry** in the sidebar
4. Use the text editor or voice controls to journal
5. Click **Back to Calendar** to return

### Managing Entries

1. Click a **green day** (day with an entry) on the calendar
2. Click **Manage Entry** in the sidebar
3. Choose from:
   - ⭐ Star/Unstar Entry
   - 👁️ Hide/Unhide Entry
   - 🗑️ Remove Entry (with confirmation)

### Logging Out

1. Click the **profile icon** (purple circle, top-right)
2. Click **Log Out**
3. Returns to the landing page

## Key Features Explained

### Date Protection
- Future dates are grayed out and disabled
- Prevents creating journal entries for days that haven't happened yet
- Today's date is highlighted with a purple ring

### Entry Indicators
- 🟢 Green square = Journal entry exists
- ⬛ Dark gray = No entry (clickable)
- ⬛ Very dark gray = Future date (disabled)
- 💜 Purple ring = Today

### Voice + Text Integration
- The AI Talk page combines both text and voice input
- Write directly in the document editor
- Or use the voice controls at the bottom
- Both methods work seamlessly together

## Development

### Project Structure
```
src/
├── App.jsx              # Main app router
├── Landing.jsx          # Landing/marketing page
├── Calendar.jsx         # Calendar view with year overview
├── AITalk.jsx          # Journal editor with voice controls
├── ProfileMenu.jsx      # User profile dropdown
├── index.css           # Tailwind CSS imports
└── main.jsx            # React entry point
```

### Styling
- Uses Tailwind CSS v4 with `@import "tailwindcss"`
- Custom gradient backgrounds
- Inter font for elegant typography
- Responsive design (mobile-friendly)

## Author

**Haider Amin**

Created: November 2025

## Future Enhancements

- Backend integration for data persistence
- Real AI voice transcription
- Entry export to PDF
- Search and filter entries
- Mood tracking analytics
- Mobile app version

## License

Private project - All rights reserved

---

Made with ❤️ by Haider Amin
