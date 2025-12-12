# Travel Agent Frontend

Modern Next.js 14 frontend for the AI Travel Agent platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: React Icons
- **Date Handling**: date-fns

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js app router pages
│   │   ├── page.tsx          # Homepage
│   │   ├── layout.tsx        # Root layout
│   │   ├── globals.css       # Global styles
│   │   ├── chat/             # Chat interface page
│   │   ├── search/           # Search page
│   │   ├── login/            # Login page
│   │   └── register/         # Register page
│   ├── components/           # Reusable React components
│   │   ├── common/           # Common UI components
│   │   ├── chat/             # Chat-related components
│   │   ├── flights/          # Flight search components
│   │   ├── hotels/           # Hotel search components
│   │   └── weather/          # Weather components
│   ├── lib/                  # Utilities and helpers
│   │   └── api.ts            # API client
│   ├── types/                # TypeScript type definitions
│   │   └── index.ts          # All type definitions
│   ├── hooks/                # Custom React hooks
│   └── store/                # Zustand state management
├── public/                   # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Available Pages

- `/` - Homepage with feature overview
- `/chat` - AI chat interface for trip planning
- `/search` - Quick search for flights and hotels
- `/login` - User login
- `/register` - User registration
- `/profile` - User profile and preferences

## API Integration

The frontend communicates with the backend API Gateway at `http://localhost:8000`.

All API calls are made through the centralized `api` client located in `src/lib/api.ts`:

```typescript
import { api } from '@/lib/api'

// Example: Search flights
const results = await api.searchFlights({
  origin: 'JFK',
  destination: 'LAX',
  departure_date: '2024-03-15',
  passengers: 2,
})
```

## Key Features

### 1. AI Chat Interface
- Real-time chat with AI travel assistant
- Conversation history
- Personalized recommendations

### 2. Flight Search
- Search flights by origin, destination, dates
- Filter by class, stops, price
- View detailed flight information

### 3. Hotel Search
- Search hotels by city and dates
- Filter by rating, price, amenities
- View hotel details and photos

### 4. Weather Information
- Current weather conditions
- 5-day forecast
- Air quality index

### 5. User Management
- Authentication with JWT
- User preferences
- Travel history

## Development Commands

```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

## Styling

This project uses Tailwind CSS for styling. The configuration is in `tailwind.config.ts`.

Custom colors, fonts, and utilities can be added in the theme extension.

## TypeScript

All components and utilities are written in TypeScript for type safety. Type definitions are centralized in `src/types/index.ts`.

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run type checking: `npm run type-check`
4. Run linting: `npm run lint`
5. Test your changes
6. Submit a pull request

## License

MIT
