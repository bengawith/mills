// frontend/src/pages/ActivateAccount.tsx
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import apiClient from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

type Status = "loading" | "success" | "error";

export default function ActivateAccountPage() {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    const activateAccount = async () => {
      if (!uid || !token) {
        setStatus("error");
        return;
      }

      try {
        await apiClient.post("/auth/users/activation/", { uid, token });
        setStatus("success");
        toast({
          title: "Account Activated!",
          description: "You can now log in with your credentials.",
        });
      } catch (error) {
        setStatus("error");
        toast({
          title: "Activation Failed",
          description: "This activation link is invalid or has expired.",
          variant: "destructive",
        });
      }
    };

    activateAccount();
  }, [uid, token, toast]);

  const renderContent = () => {
    switch (status) {
      case "loading":
        return (
          <div className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
            <p className="text-muted-foreground">Activating your account...</p>
          </div>
        );
      case "success":
        return (
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <CheckCircle className="w-12 h-12 text-green-500" />
            <p className="text-foreground">Your account has been successfully activated!</p>
            <Button onClick={() => navigate("/login")} className="w-full">
              Proceed to Login
            </Button>
          </div>
        );
      case "error":
        return (
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <XCircle className="w-12 h-12 text-destructive" />
            <p className="text-foreground">There was an error activating your account.</p>
            <p className="text-muted-foreground text-sm">The link may be expired or invalid. Please try registering again.</p>
            <Button onClick={() => navigate("/register")} className="w-full" variant="outline">
              Go to Registration
            </Button>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-primary-glow/5 px-4">
      <Card className="w-full max-w-md shadow-xl border-0 bg-card/80 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Account Activation</CardTitle>
          <CardDescription className="text-center">
            Finalising your Mill Dash account setup
          </CardDescription>
        </CardHeader>
        <CardContent className="py-8">
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
}