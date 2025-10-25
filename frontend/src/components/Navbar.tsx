
import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Menu, X, LogOut, Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    // Check auth status
    supabase.auth.getSession().then(({ data: { session } }) => {
      setIsAuthenticated(!!session);
      setIsLoadingAuth(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsAuthenticated(!!session);
      setIsLoadingAuth(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    // Prevent background scrolling when menu is open
    document.body.style.overflow = !isMenuOpen ? 'hidden' : '';
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    
    // Close mobile menu if open
    if (isMenuOpen) {
      setIsMenuOpen(false);
      document.body.style.overflow = '';
    }
  };

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      
      // Clear cached data
      sessionStorage.clear();
      
      toast.success('Logged out successfully');
      navigate('/');
      
      if (isMenuOpen) {
        setIsMenuOpen(false);
        document.body.style.overflow = '';
      }
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to logout');
    }
  };

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 py-2 sm:py-3 md:py-4 transition-all duration-300",
        isScrolled 
          ? "bg-white/95 backdrop-blur-md shadow-sm" 
          : "bg-white/10 backdrop-blur-sm"
      )}
    >
      <div className="container flex items-center justify-between px-4 sm:px-6 lg:px-8">
        <a 
          href="#" 
          className="flex items-center space-x-2"
          onClick={(e) => {
            e.preventDefault();
            scrollToTop();
          }}
          aria-label="ClauseBot.Ai"
        >
          <img 
            src="/clausebot-icon.svg" 
            alt="ClauseBot.Ai Logo" 
            className="h-8 sm:h-9" 
          />
        </a>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <nav className="flex space-x-8">
            <a 
              href="#" 
              className={cn(
                "relative py-2 transition-colors duration-300 font-medium",
                isScrolled 
                  ? "text-gray-800 hover:text-primary after:bg-primary" 
                  : "text-white hover:text-white/80 after:bg-white",
                "after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:transition-all hover:after:w-full"
              )}
              onClick={(e) => {
                e.preventDefault();
                scrollToTop();
              }}
            >
              Home
            </a>
            {isLoadingAuth ? (
              <Loader2 className={cn(
                "h-4 w-4 animate-spin",
                isScrolled ? "text-gray-400" : "text-white/60"
              )} />
            ) : isAuthenticated ? (
              <>
                <a 
                  href="/dashboard" 
                  className={cn(
                    "relative py-2 transition-colors duration-300 font-medium",
                    isScrolled 
                      ? "text-gray-800 hover:text-primary after:bg-primary" 
                      : "text-white hover:text-white/80 after:bg-white",
                    "after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:transition-all hover:after:w-full"
                  )}
                >
                  Dashboard
                </a>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className={cn(
                    "gap-2",
                    isScrolled ? "text-gray-800 hover:text-primary" : "text-white hover:text-white/80"
                  )}
                  data-qa="logout-button"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </>
            ) : (
              <a 
                href="/auth" 
                className={cn(
                  "relative py-2 transition-colors duration-300 font-medium",
                  isScrolled 
                    ? "text-gray-800 hover:text-primary after:bg-primary" 
                    : "text-white hover:text-white/80 after:bg-white",
                  "after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:transition-all hover:after:w-full"
                )}
                data-qa="signin-button"
              >
                Sign In
              </a>
            )}
            <a 
              href="#features" 
              className={cn(
                "relative py-2 transition-colors duration-300 font-medium",
                isScrolled 
                  ? "text-gray-800 hover:text-primary after:bg-primary" 
                  : "text-white hover:text-white/80 after:bg-white",
                "after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:transition-all hover:after:w-full"
              )}
            >
              About
            </a>
            <a 
              href="#details" 
              className={cn(
                "relative py-2 transition-colors duration-300 font-medium",
                isScrolled 
                  ? "text-gray-800 hover:text-primary after:bg-primary" 
                  : "text-white hover:text-white/80 after:bg-white",
                "after:absolute after:bottom-0 after:left-0 after:h-[2px] after:w-0 after:transition-all hover:after:w-full"
              )}
            >
              Contact
            </a>
          </nav>
          
          <a 
            href="https://www.miltmonndt.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className={cn(
              "inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-full transition-all duration-300",
              isScrolled
                ? "text-white bg-primary hover:bg-primary/90"
                : "text-white bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30"
            )}
          >
            Back to MiltmonNDT
          </a>
        </div>

        {/* Mobile menu button - increased touch target */}
        <button 
          className={cn(
            "md:hidden p-3 focus:outline-none transition-colors",
            isScrolled ? "text-gray-700" : "text-white"
          )}
          onClick={toggleMenu}
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation - improved for better touch experience */}
      <div className={cn(
        "fixed inset-0 z-40 bg-white flex flex-col pt-16 px-6 md:hidden transition-all duration-300 ease-in-out",
        isMenuOpen ? "opacity-100 translate-x-0" : "opacity-0 translate-x-full pointer-events-none"
      )}>
        <nav className="flex flex-col space-y-8 items-center mt-8">
          <a 
            href="#" 
            className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
            onClick={(e) => {
              e.preventDefault();
              scrollToTop();
              setIsMenuOpen(false);
              document.body.style.overflow = '';
            }}
          >
            Home
          </a>
          {isLoadingAuth ? (
            <div className="flex justify-center py-3">
              <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
            </div>
          ) : isAuthenticated ? (
            <>
              <a 
                href="/dashboard" 
                className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
                onClick={() => {
                  setIsMenuOpen(false);
                  document.body.style.overflow = '';
                }}
              >
                Dashboard
              </a>
              <Button
                variant="ghost"
                size="lg"
                onClick={handleLogout}
                className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100 gap-2"
                data-qa="logout-button-mobile"
              >
                <LogOut className="h-5 w-5" />
                Logout
              </Button>
            </>
          ) : (
            <a 
              href="/auth" 
              className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
              onClick={() => {
                setIsMenuOpen(false);
                document.body.style.overflow = '';
              }}
              data-qa="signin-button-mobile"
            >
              Sign In
            </a>
          )}
          <a 
            href="#features" 
            className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
            onClick={() => {
              setIsMenuOpen(false);
              document.body.style.overflow = '';
            }}
          >
            About
          </a>
          <a 
            href="#details" 
            className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
            onClick={() => {
              setIsMenuOpen(false);
              document.body.style.overflow = '';
            }}
          >
            Contact
          </a>
          <a 
            href="/admin"
            className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" 
            onClick={() => {
              setIsMenuOpen(false);
              document.body.style.overflow = '';
            }}
          >
            Admin
          </a>
          
          <a 
            href="https://www.miltmonndt.com/"
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center px-6 py-3 text-lg font-medium text-white bg-primary hover:bg-primary/90 rounded-full transition-colors w-full text-center"
            onClick={() => {
              setIsMenuOpen(false);
              document.body.style.overflow = '';
            }}
          >
            Back to MiltmonNDT
          </a>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
