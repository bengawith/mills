# MillDash Frontend Documentation

## Overview
MillDash is a comprehensive maintenance management dashboard for industrial environments. The frontend is built with React and TypeScript, using React Query for data fetching, custom UI components for consistent design, and Tailwind CSS for responsive layouts. This documentation provides a detailed guide to the structure, components, and usage patterns of the frontend codebase.

---

## Directory Structure

- **src/**
  - **App.tsx, main.tsx**: Entry points for the React application.
  - **components/**: Reusable UI components (Card, Button, Input, etc.).
  - **contexts/**: React context providers for global state management.
  - **hooks/**: Custom React hooks (e.g., use-toast).
  - **lib/**: API utilities and constants.
  - **pages/**: Main application pages, organized by feature:
    - **Dashboard/**: Dashboard views and widgets.
    - **MaintenanceHub/**: Maintenance management features.
      - **ManageTickets/**: Ticket management components (detailed below).
    - **OperatorTerminal/**: Operator-facing controls and status.
  - **test/**: Frontend test files.

---

## Key Technologies
- **React**: Functional components, hooks, context API.
- **TypeScript**: Strict type checking, explicit type annotations throughout.
- **React Query**: Data fetching, caching, and mutation.
- **Tailwind CSS**: Utility-first styling for responsive layouts.
- **Lucide Icons**: Iconography for UI clarity.

---

## Main Components & Features

### Dashboard
- Provides real-time analytics, machine status, and performance metrics.
- Uses custom widgets and charts for data visualization.

### MaintenanceHub
- Central hub for managing maintenance tickets, work notes, images, and components.
- **ManageTickets/** contains the following thoroughly documented components:

#### TicketDetailView.tsx
- Displays detailed information for a maintenance ticket.
- Allows status updates (with confirmation for resolving tickets).
- Integrates WorkNotesSection, ImageSection, and ComponentLogSection.
- Uses React Query for fetching and updating ticket data.

#### WorkNotesSection.tsx
- Lists all work notes attached to a ticket.
- Provides a form to add new notes.
- Uses mutation and query invalidation for real-time updates.

#### ImageSection.tsx
- Displays all images attached to a ticket.
- Allows uploading new images via file input.
- Uses mutation for uploads and query invalidation for refresh.

#### ComponentLogSection.tsx
- Lists all components used for a ticket.
- Provides a form to log new component usage from inventory.
- Fetches inventory components and updates stock on mutation.

#### TicketInsights.tsx
- Provides analytics and insights for a ticket (e.g., time to resolve, note count).
- Uses custom UI components for visualization.

---

## API Integration
- All data operations (fetching, updating, uploading) are handled via functions in `lib/api.ts`.
- React Query is used for caching and mutation, ensuring efficient and up-to-date UI.

---

## Type Safety & Comments
- All components and functions use explicit TypeScript type annotations.
- Verbose file-level and inline comments are present throughout the codebase for maintainability and clarity.
- Props interfaces are exported for reuse and documentation.

---

## UI/UX Patterns
- Consistent use of custom UI components for cards, forms, tables, and dialogs.
- Responsive layouts using Tailwind CSS grid and spacing utilities.
- Toast notifications for user feedback on actions (success, error, validation).
- Confirmation dialogs for critical actions (e.g., resolving tickets).

---

## Extending & Customizing
- New features can be added by creating new components in the relevant directory and following the established patterns for type safety, comments, and UI consistency.
- API endpoints should be added to `lib/api.ts` and integrated using React Query.

---

## Testing
- Frontend tests are located in `src/test/` and use standard React testing libraries.
- All business logic and UI interactions should be covered by tests for reliability.

---

## Backend Integration
- The frontend communicates with the backend via RESTful API endpoints.
- Backend features include ticket management, user authentication, analytics, and inventory control.

---

## Contribution Guidelines
- Follow TypeScript best practices and maintain explicit type annotations.
- Add verbose comments for all new code.
- Use custom UI components for consistency.
- Ensure all new features are covered by tests.

---

## Contact & Support
For questions, feature requests, or bug reports, please contact the repository owner or open an issue on GitHub.

---

This documentation covers the frontend. For backend details, see the backend documentation or README in the `backend/` directory.
