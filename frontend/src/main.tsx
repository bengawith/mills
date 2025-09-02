// frontend/src/main.tsx
/**
 * Entry point for the React application.
 * Sets up React root, routing, and authentication context provider.
 * All pages/components are rendered within <App />.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { AuthProvider } from './contexts/AuthContext';
import { BrowserRouter } from "react-router-dom";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider> { /* Wrap App with AuthProvider */ }
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);