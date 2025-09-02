/*
  Login.tsx - MillDash Frontend Authentication Page

  This file implements the login page for the MillDash application using React and TypeScript. It provides a user interface for users to sign in to their accounts, handling authentication via the AuthContext and displaying feedback using a toast notification system. The component is designed with accessibility and user experience in mind, featuring password visibility toggling, error handling, and navigation to registration and password recovery pages.

  Key Features:
  - Uses React functional component with hooks for state management (email, password, loading, password visibility).
  - Integrates with AuthContext to perform authentication and handle login logic.
  - Displays toast notifications for success and error feedback.
  - Utilizes custom UI components for consistent styling (Button, Input, Label, Card, etc.).
  - Provides navigation to registration and password recovery routes using React Router.
  - Implements password visibility toggle for improved UX.
  - Handles backend error responses and displays user-friendly messages.
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is a core part of the authentication flow, ensuring secure and user-friendly access to the MillDash platform.
*/

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom"; // Import useNavigate
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Factory, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext"; // Import the useAuth hook


export default function Login() {
  // State for storing the user's email input
  const [email, setEmail] = useState<string>("");
  // State for storing the user's password input
  const [password, setPassword] = useState<string>("");
  // State to toggle password visibility
  const [showPassword, setShowPassword] = useState<boolean>(false);
  // State to indicate loading status during login
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // AuthContext hook provides login function
  const { login } = useAuth();
  // React Router hook for navigation after login
  const navigate = useNavigate();

  /**
   * Handles the login form submission.
   * Prevents default form behavior, sets loading state, and attempts authentication.
   * Displays toast notifications for success or error feedback.
   * @param e - React form event
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // Attempt login using AuthContext
      await login({ email, password });
      toast({
        title: "Login successful",
        description: "Welcome back!",
      });
    } catch (error: any) {
      // Handle errors from backend or network
      console.error("Login failed:", error);
      const errorData = error.response?.data;
      let errorMessage: string = "Please check your email and password."; // Default message
      if (errorData) {
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.email) {
          errorMessage = `Email: ${errorData.email[0]}`;
        } else if (errorData.password) {
          errorMessage = `Password: ${errorData.password[0]}`;
        }
        // Log the full error response for debugging
        console.error("Backend Error Response:", error.response);
      }
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    // Main container centers the login card and applies background gradient
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-primary-glow/5 px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Logo and Header Section */}
        <div className="text-center">
          {/* Factory icon inside a styled container */}
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary to-primary-glow rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            <Factory className="w-8 h-8 text-primary-foreground" />
          </div>
          <h2 className="text-3xl font-bold text-foreground">Welcome back</h2>
          <p className="text-muted-foreground mt-2">Sign in to your MillDash account</p>
        </div>

        {/* Login Form Card */}
        <Card className="shadow-xl border-0 bg-card/80 backdrop-blur">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign in</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          {/* Form for user login */}
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {/* Email input field */}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="john@company.com"
                  value={email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                  required
                  className="transition-all focus:ring-2 focus:ring-primary/20"
                />
              </div>
              {/* Password input field with visibility toggle */}
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                    required
                    className="pr-10 transition-all focus:ring-2 focus:ring-primary/20"
                  />
                  {/* Button to toggle password visibility */}
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              {/* Remember me checkbox and forgot password link */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <input
                    id="remember"
                    type="checkbox"
                    className="rounded border-input"
                  />
                  <Label htmlFor="remember" className="text-sm">Remember me</Label>
                </div>
                <Link to="/forgot-password" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              {/* Submit button for login */}
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-primary to-primary-glow hover:from-primary/90 hover:to-primary-glow/90 transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? "Signing in..." : "Sign in"}
              </Button>
              {/* Link to registration page */}
              <div className="text-center text-sm text-muted-foreground">
                Don't have an account?{" "}
                <Link to="/register" className="text-primary hover:underline font-medium">
                  Sign up
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}