import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import HomePage from "./pages/HomePage";
import ActivateAccountPage from "./pages/ActivateAccount";
import NotFound from "./pages/NotFound";
import ResetPasswordConfirmPage from "./pages/ResetPasswordConfirmPage";
import CompleteProfilePage from "./pages/CompleteProfilePage";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard/index";
import MaintenanceHub from "./pages/MaintenanceHub";
import LogNewTicket from "./pages/LogNewTicket";
import ManageTickets from "./pages/ManageTickets/index";
import OperatorTerminal from "./pages/OperatorTerminal";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/activate/:uid/:token" element={<ActivateAccountPage />} />

          <Route path="/reset-password/:uid/:token" element={<ResetPasswordConfirmPage />} />

          {/* Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/complete-profile" element={<CompleteProfilePage />} />
          
          {/* Protected Routes with Layout */}
          <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          <Route path="/maintenance-hub" element={<Layout><MaintenanceHub /></Layout>} />
          <Route path="/log-ticket" element={<Layout><LogNewTicket /></Layout>} />
          <Route path="/manage-tickets" element={<Layout><ManageTickets /></Layout>} />
          <Route path="/operator-terminal" element={<Layout><OperatorTerminal /></Layout>} />

          {/* Not Found catch-all */}
          <Route path="*" element={<NotFound />} />
        </Routes>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;