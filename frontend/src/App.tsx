import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PWAUpdatePrompt from "@/components/PWAUpdatePrompt";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Academy from "./pages/Academy";
import AcademyOnboarding from "./pages/AcademyOnboarding";
import WeldTrackFoundation from "./pages/WeldTrackFoundation";
import Professional from "./pages/Professional";
import Demo from "./pages/Demo";
import Pricing from "./pages/Pricing";
import Checkout from "./pages/Checkout";
import Auth from "./pages/Auth";
import Admin from "./pages/Admin";
import Dashboard from "./pages/Dashboard";
import ClauseBot from "./pages/ClauseBot";
import KnowledgeBase from "./pages/KnowledgeBase";
import Health from "./pages/Health";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <PWAUpdatePrompt />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Index />} />
          <Route path="/academy" element={<Academy />} />
          <Route path="/academy/onboarding" element={<AcademyOnboarding />} />
          <Route path="/academy/weldtrack-foundation" element={<WeldTrackFoundation />} />
          <Route path="/professional" element={<Professional />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/health" element={<Health />} />
          
          {/* Auth route */}
          <Route path="/auth" element={<Auth />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
          <Route path="/kb" element={<ProtectedRoute><KnowledgeBase /></ProtectedRoute>} />
          <Route path="/clausebot" element={<ProtectedRoute><ClauseBot /></ProtectedRoute>} />
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
