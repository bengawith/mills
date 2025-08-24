import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Gauge, Settings, Lock, Activity } from "lucide-react"; // Updated icons
import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/20 via-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Mill Dash
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Streamline your manufacturing operations with our comprehensive platform. Track machine data, manage maintenance, and optimize production with ease.
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
              <Gauge className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Machine Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Monitor machine performance, uptime, and utilization in real-time to identify bottlenecks.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Settings className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Maintenance Management</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Efficiently manage maintenance tickets, track repairs, and schedule preventative maintenance.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Lock className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Secure & Reliable</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Ensure data integrity and operational security with robust access controls and encrypted data storage.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <Activity className="h-8 w-8 text-primary mb-2" />
              <CardTitle className="text-xl">Production Optimization</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                Optimize production schedules, track output, and minimize downtime with actionable insights.
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to optimize your manufacturing?</h2>
          <Link to="/register">
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