import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, DollarSign, Shield, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/20 via-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            TimePay
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Streamline your payroll management with our comprehensive platform. Track time, manage employees, and process payments with ease.
          </p>
          <Link to="/register">
            <Button size="lg" className="text-lg px-8 py-4">
              Get Started
            </Button>
          </Link>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Clock className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Time Tracking</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Employees can easily log their working hours with detailed descriptions and automatic approval workflows.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <DollarSign className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Payroll Management</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Automated payroll calculations with tax deductions, NI contributions, and instant payslip generation.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Shield className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Secure & Compliant</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Bank-level security with GDPR compliance and encrypted data storage to protect sensitive information.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Zap className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Real-time Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Live dashboard with analytics, employee metrics, and comprehensive reporting for better decision making.
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to streamline your payroll?</h2>
          <Link to="/auth">
            <Button variant="outline" size="lg" className="text-lg px-8 py-4">
              Sign Up Now
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomePage;