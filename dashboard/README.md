# HUMBEX Dashboard

## Overview

This directory is a placeholder for the future Next.js dashboard application.

## Planned Features

- User authentication and registration
- Subscription management
- API key management (encrypted storage)
- Trading signal history
- Order history and analytics
- Account balance monitoring
- Real-time notifications

## Technology Stack (Planned)

- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React + Tailwind CSS
- **State Management**: React Query / Zustand
- **Charts**: Recharts / TradingView widgets
- **API Client**: Axios / Fetch
- **Authentication**: JWT tokens

## Development (Future)

```bash
cd dashboard
npm install
npm run dev
```

Dashboard will be available at `http://localhost:3000`

## Integration

The dashboard will communicate with the backend API at:
- Local: `http://localhost:8000`
- Production: `https://api.humbex.com`

## Security

- All API keys encrypted before transmission
- HTTPS only in production
- JWT-based authentication
- CORS configured for frontend domain only
