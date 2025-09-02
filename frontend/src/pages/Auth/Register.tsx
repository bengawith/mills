/*
  Register.tsx - MillDash Frontend User Registration Page

  This file implements the registration page for the MillDash application using React and TypeScript. It provides a user interface for new users to create an account, handling form validation, password confirmation, and backend integration via the API client. The component is designed for accessibility and user experience, featuring password visibility toggling, error handling, and navigation to login and legal pages.

  Key Features:
  - Uses React functional component with hooks for state management (form data, loading, password visibility).
  - Validates password confirmation before submitting registration.
  - Integrates with backend API to create new user accounts.
  - Displays toast notifications for success and error feedback.
  - Utilizes custom UI components for consistent styling (Button, Input, Label, Card, etc.).
  - Provides navigation to login, terms, and privacy routes using React Router.
  - Implements password visibility toggle for improved UX.
  - Handles backend error responses and displays user-friendly messages.
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is a core part of the onboarding flow, ensuring secure and user-friendly account creation for the MillDash platform.
*/

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom"; // Import useNavigate
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Factory, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/lib/api"; // Import our API client

export default function Register() {
  // State for storing registration form data
  const [formData, setFormData] = useState<{
    fullName: string;
    email: string;
    password: string;
    confirmPassword: string;
    role: string;
    companyName: string;
  }>({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "admin",
    companyName: "",
  });
  // State to toggle password visibility
  const [showPassword, setShowPassword] = useState<boolean>(false);
  // State to toggle confirm password visibility
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  // State to indicate loading status during registration
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // React Router hook for navigation after registration
  const navigate = useNavigate();

  /**
   * Handles input changes for the registration form fields.
   * Updates the corresponding field in the formData state.
   * @param field - The field name to update
   * @param value - The new value for the field
   */
  const handleInputChange = (field: string, value: string): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  /**
   * Handles the registration form submission.
   * Validates password confirmation, prepares payload, and sends registration request to backend.
   * Displays toast notifications for success or error feedback.
   * @param e - React form event
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Password mismatch",
        description: "Passwords do not match. Please try again.",
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);
    // Split full name into first and last name for the API
    const nameParts = formData.fullName.split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts.slice(1).join(' ');
    const payload = {
      first_name: firstName,
      last_name: lastName || firstName, // Handle single-name entries
      email: formData.email,
      password: formData.password,
      re_password: formData.confirmPassword,
      role: formData.role.toUpperCase(), // API expects "ADMIN"
    };
    try {
      await apiClient.post("/auth/users/", payload);
      toast({
        title: "Account created successfully",
        description: "Welcome to TimePay! Please check your email to verify your account.",
      });
      // Redirect to login page after successful registration
      navigate("/login");
    } catch (error: any) {
      const errorData = error.response?.data;
      let errorMessage: string = "An unknown error occurred.";
      // Extract more specific error messages from the backend if available
      if (errorData) {
        if (errorData.email) errorMessage = `Email: ${errorData.email[0]}`;
        else if (errorData.password) errorMessage = `Password: ${errorData.password[0]}`;
      }
      toast({
        title: "Registration Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-primary-glow/5 px-4 py-8">
      <div className="w-full max-w-md space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary to-primary-glow rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            <Factory className="w-8 h-8 text-primary-foreground" />
          </div>
          <h2 className="text-3xl font-bold text-foreground">Create account</h2>
          <p className="text-muted-foreground mt-2">Join TimePay and streamline your payroll</p>
        </div>

        {/* Registration Form (No visual changes here) */}
        <Card className="shadow-xl border-0 bg-card/80 backdrop-blur">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign up</CardTitle>
            <CardDescription className="text-center">
              Create your TimePay account
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="John Doe"
                  value={formData.fullName}
                  onChange={(e) => handleInputChange("fullName", e.target.value)}
                  required
                  className="transition-all focus:ring-2 focus:ring-primary/20"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="john@company.com"
                  value={formData.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  required
                  className="transition-all focus:ring-2 focus:ring-primary/20"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="companyName">Company Name</Label>
                <Input
                  id="companyName"
                  type="text"
                  placeholder="Acme Corporation"
                  value={formData.companyName}
                  onChange={(e) => handleInputChange("companyName", e.target.value)}
                  required
                  className="transition-all focus:ring-2 focus:ring-primary/20"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    required
                    className="pr-10 transition-all focus:ring-2 focus:ring-primary/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    required
                    className="pr-10 transition-all focus:ring-2 focus:ring-primary/20"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  id="terms"
                  type="checkbox"
                  className="rounded border-input"
                  required
                />
                <Label htmlFor="terms" className="text-sm">
                  I agree to the{" "}
                  <Link to="/terms" className="text-primary hover:underline">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link to="/privacy" className="text-primary hover:underline">
                    Privacy Policy
                  </Link>
                </Label>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-primary to-primary-glow hover:from-primary/90 hover:to-primary-glow/90 transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? "Creating account..." : "Create account"}
              </Button>
              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="text-primary hover:underline font-medium">
                  Sign in
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}