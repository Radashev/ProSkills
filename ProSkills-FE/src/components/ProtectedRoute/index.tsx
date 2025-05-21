import { Navigate, Outlet } from "react-router";
import { useAuthStore } from "../../store/useAuthStore";
import { PATHS } from "../../routes/paths";
import { GUEST_ROLE } from "../../models/User";

const ProtectedRoute: React.FC<{
  allowedRoles: readonly string[];
  children?: React.ReactNode;
}> = ({ allowedRoles, children }) => {
  const role = useAuthStore((state) => state.user?.role) || GUEST_ROLE;

  if (!allowedRoles.includes(role)) {
    return <Navigate to={PATHS.HOME.link} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};

export default ProtectedRoute;
