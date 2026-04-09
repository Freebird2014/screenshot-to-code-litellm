import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/auth-store";
import { Loader2 } from "lucide-react";

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, verifyToken } = useAuthStore();
  const location = useLocation();
  const [isVerifying, setIsVerifying] = useState(true);
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    const checkToken = async () => {
      if (!isAuthenticated) {
        setIsVerifying(false);
        return;
      }

      // Verify token with backend
      const valid = await verifyToken();
      setIsValid(valid);
      setIsVerifying(false);
    };

    checkToken();
  }, [isAuthenticated, verifyToken]);

  if (isVerifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-zinc-950">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 dark:text-blue-400" />
          <p className="text-sm text-gray-500 dark:text-gray-400">Verifying session...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !isValid) {
    // Redirect to login page, preserving the intended destination
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
