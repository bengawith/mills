import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route } from "react-router-dom";
import { WebSocketProvider } from "@/contexts/WebSocketContext";
import Login from "./pages/Auth/Login";
import ActivateAccountPage from "./pages/Auth/ActivateAccount";
import NotFound from "./pages/NotFound";
import ResetPasswordConfirmPage from "./pages/Auth/ResetPasswordConfirmPage";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import MaintenanceHub from "./pages/MaintenanceHub";
import OperatorTerminal from "./pages/OperatorTerminal";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <WebSocketProvider autoConnect={true}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
          <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Login />} />
          <Route path="/activate/:uid/:token" element={<ActivateAccountPage />} />

          <Route path="/reset-password/:uid/:token" element={<ResetPasswordConfirmPage />} />

          {/* Auth Routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes with Layout */}
          <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          <Route path="/maintenance-hub" element={<Layout><MaintenanceHub /></Layout>} />
          <Route path="/operator-terminal" element={<Layout><OperatorTerminal /></Layout>} />

          {/* Not Found catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </TooltipProvider>
    </WebSocketProvider>
  </QueryClientProvider>
);

export default App;