import { redirect } from "react-router";
import { PATHS } from "../../routes/paths";
import { useAuthStore } from "../../store/useAuthStore";

export async function action() {
  const { logout } = useAuthStore.getState();
  await logout();

  return redirect(PATHS.AUTH.link);
}
