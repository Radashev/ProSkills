import axios, { AxiosError, AxiosResponse } from "axios";
import { LoaderFunction, redirect } from "react-router";
import { PATHS, ROLE_PATHS } from "../routes/paths";
import {
  UserRegistration,
  UserLogin,
  UserRoles,
  GUEST_ROLE,
} from "../models/User";
import {
  RegisterFormData,
  LoginFormData,
  AuthRequestType,
} from "../models/Auth";
import { APIError } from "../models/APIResponse";
import { useAuthStore } from "../store/useAuthStore";
import { ArgsProps } from "antd/es/notification";
import { handleAxiosError } from "./axiosUtils";
import { capitalizeFirstLetter } from "./stringUtils";
import { NotificationInstance } from "antd/es/notification/interface";
import { authApi } from "../api/auth";

export const getRequestBody = {
  register: (formData: RegisterFormData) => {
    const userBody: UserRegistration = {
      email: formData.email,
      first_name: formData.first_name || "",
      last_name: formData.last_name || "",
      password: formData.password,
      role: UserRoles.STUDENT,
    };

    return userBody;
  },
  login: (formData: LoginFormData) => {
    const userBody: UserLogin = {
      email: formData.email,
      password: formData.password,
    };

    return userBody;
  },
};

export const handleAuthResponse = async (
  response: AxiosResponse | AxiosError<APIError>,
  mode: AuthRequestType,
  userRoleToCreate: UserRoles,
  notification: NotificationInstance,
  navigate: any
) => {
  const { loginAttempts, incrementLoginAttempts, resetLoginAttempts } =
    useAuthStore.getState();

  let notificationConfig: ArgsProps = {
    message: `${capitalizeFirstLetter(mode)} Attempt Unsuccessful`,
    description: `Unable to ${mode}`,
    placement: "topRight",
    duration: 10,
  };

  if (!axios.isAxiosError(response)) {
    if (mode === "login") {
      resetLoginAttempts();

      const { data } = await authApi.getToken();
      useAuthStore.getState().setUser(data);

      navigate(PATHS.HOME.link);
      return;
    }

    if (userRoleToCreate !== UserRoles.STUDENT) {
      notification.success({
        ...notificationConfig,
        message: `${capitalizeFirstLetter(mode)} Attempt Successful`,
        description: `The user of ${userRoleToCreate} role was created`,
      });
    }

    navigate(PATHS.AUTH.link);
  } else {
    if (mode === "login") {
      incrementLoginAttempts();
    }

    handleAxiosError(response, notification, notificationConfig);
  }
};

export const rootLoader: LoaderFunction = async ({ request }) => {
  const { checkAuth, isAuthenticated } = useAuthStore.getState();
  const guestAccessiblePaths = new Set(ROLE_PATHS[GUEST_ROLE] || []);
  const pathname = new URL(request.url).pathname;
  const currentPath =
    pathname.startsWith("/") && pathname !== PATHS.HOME.link
      ? pathname.substring(1)
      : pathname;

  if (guestAccessiblePaths.has(currentPath)) {
    return null;
  }

  if (!isAuthenticated) {
    try {
      await checkAuth();
    } catch {
      if (!guestAccessiblePaths.has(currentPath)) {
        return redirect(PATHS.AUTH.link);
      }
    }
  }

  return null;
};

