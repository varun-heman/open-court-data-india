# Open Court Data India - Frontend

A modern web interface for accessing and visualizing Indian court data.

## Overview

This frontend application provides a user-friendly interface to browse and search through court data collected by the Open Court Data India scrapers. The interface is designed to be intuitive, responsive, and visually appealing, making it easy to navigate through cause lists, judgments, and other court documents.

## Features

- **Modern UI**: Built with React and Tailwind CSS for a clean, responsive interface
- **Court Navigation**: Browse different courts through an intuitive sidebar menu
- **Document Types**: Separate sections for cause lists, judgments, and other document types
- **Date Navigation**: Calendar-based navigation to view court data for specific dates
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Filtering & Sorting**: Filter and sort court data based on various parameters

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/                 # Source code
│   ├── components/      # React components
│   ├── services/        # API services
│   ├── assets/          # Images, icons, etc.
│   ├── App.js           # Main application component
│   └── index.js         # Application entry point
├── package.json         # Dependencies and scripts
└── tailwind.config.js   # Tailwind CSS configuration
```

## Installation

1. Ensure you have Node.js (v14 or newer) installed on your system
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Development

To start the development server:

```bash
npm start
```

This will start the application in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Building for Production

To create a production build:

```bash
npm run build
```

This will create an optimized build in the `build` folder that can be deployed to a web server.

## Integration with Backend

This frontend is designed to work with the Open Court Data India scrapers. The application fetches data from the backend API endpoints to display court information. In development mode, it uses mock data to simulate the API responses.

## Customization

### Styling

The application uses Tailwind CSS for styling. You can customize the appearance by modifying the `tailwind.config.js` file.

### Adding New Courts

To add a new court to the sidebar menu, update the `Sidebar.js` component with the new court information.

## License

This project is part of the Open Court Data India initiative. See the main project repository for licensing information.
