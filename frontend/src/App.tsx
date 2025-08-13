import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { Toaster } from './components/ui/Toaster';

function App() {
  return (
    <AuthProvider>
      <Main />
      <Toaster />
    </AuthProvider>
  );
}

// Main component to decide which page to show based on auth state
const Main = () => {
  const { token } = useAuth();
  return token ? <DashboardPage /> : <LoginPage />;
};

export default App;