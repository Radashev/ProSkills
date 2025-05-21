import { useSearchParams } from "react-router";
import Login from "../../components/Login";
import Register from "../../components/Register";

const AuthPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const mode = searchParams.get("mode");

  return <>{mode === "register" ? <Register /> : <Login />}</>;
};

export default AuthPage;
