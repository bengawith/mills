/*
  ResetPasswordConfirmPage.tsx - MillDash Frontend Password Reset Confirmation Page

  This file implements the password reset confirmation page for the MillDash application using React and TypeScript. It provides a user interface for users to set a new password after receiving a reset link, handling form validation, password confirmation, and backend integration via the API client. The component is designed for accessibility and user experience, featuring password visibility toggling, error handling, and navigation to the login page.

  Key Features:
  - Uses React functional component with hooks for state management (new password, confirm password, loading, password visibility).
  - Validates password confirmation before submitting the reset request.
  - Integrates with backend API to reset the user's password using UID and token from the URL.
  - Displays toast notifications for success and error feedback.
  - Utilizes custom UI components for consistent styling (Button, Input, Label, Card, etc.).
  - Provides navigation to login after successful reset.
  - Implements password visibility toggle for improved UX.
  - Handles backend error responses and displays user-friendly messages.
  - Responsive and visually appealing layout using Tailwind CSS utility classes.

  This component is a core part of the password recovery flow, ensuring secure and user-friendly password reset for the MillDash platform.
*/

// frontend/src/pages/ResetPasswordConfirmPage.tsx
import { useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Factory, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import apiClient from "@/lib/api";

export default function ResetPasswordConfirmPage() {
  // State for storing the new password input
  const [newPassword, setNewPassword] = useState<string>("");
  // State for storing the confirm password input
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  // State to toggle new password visibility
  const [showPassword, setShowPassword] = useState<boolean>(false);
  // State to toggle confirm password visibility
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  // State to indicate loading status during password reset
  const [isLoading, setIsLoading] = useState<boolean>(false);
  // Toast notification handler for user feedback
  const { toast } = useToast();
  // React Router hook for navigation after password reset
  const navigate = useNavigate();
  // Get UID and Token from the URL params
  const { uid, token } = useParams<{ uid?: string; token?: string }>();

  /**
   * Handles the password reset form submission.
   * Validates password confirmation, prepares payload, and sends reset request to backend.
   * Displays toast notifications for success or error feedback.
   * @param e - React form event
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast({
        title: "Password mismatch",
        description: "The passwords do not match. Please try again.",
        variant: "destructive",
      });
      return;
    }
    if (!uid || !token) {
      toast({
        title: "Invalid Link",
        description: "The password reset link is incomplete.",
        variant: "destructive",
      });
      return;
    }
    setIsLoading(true);
    const payload = {
      uid,
      token,
      new_password: newPassword,
      re_new_password: confirmPassword,
    };
    try {
      await apiClient.post("/auth/users/reset_password_confirm/", payload);
      toast({
        title: "Password Reset Successful",
        description: "You can now log in with your new password.",
      });
      navigate("/login");
    } catch (error: any) {
      toast({
        title: "Password Reset Failed",
        description: "This link may be invalid or expired. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-primary-glow/5 px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary to-primary-glow rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            <Factory className="w-8 h-8 text-primary-foreground" />
          </div>
          <h2 className="text-3xl font-bold text-foreground">Reset Your Password</h2>
          <p className="text-muted-foreground mt-2">Enter a new password for your TimePay account</p>
        </div>

        <Card className="shadow-xl border-0 bg-card/80 backdrop-blur">
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <div className="relative">
                  <Input
                    id="newPassword"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter new password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
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
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
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
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-primary to-primary-glow hover:from-primary/90 hover:to-primary-glow/90 transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? "Resetting Password..." : "Reset Password"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}