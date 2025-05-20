import { UserLogin, UserRegistration, UserRoles } from "../models/User";
import { RegisterFormData, LoginFormData } from "../models/Auth";
import { getRequestBody } from "../utils/authUtils";
import { getAxiosError } from "../utils/axiosUtils";
import api from ".";
import { urls } from "./urls";

const AUTH_BASE_URL = "/auth";
const requestUrls = urls.auth;

const getAuthUrl = (path: string) => `${AUTH_BASE_URL}${path}`;

export const authApi = {
  register: async (formData: RegisterFormData, userRole: UserRoles) => {
    const body: UserRegistration = getRequestBody.register(formData);

    try {
      return await api.post(getAuthUrl(requestUrls.register[userRole]), body);
    } catch (error: unknown) {
      return getAxiosError(error);
    }
  },
  login: async (formData: LoginFormData) => {
    const body: UserLogin = getRequestBody.login(formData);

    try {
      return await api.post(getAuthUrl(requestUrls.login), body);
    } catch (error: unknown) {
      return getAxiosError(error);
    }
  },
  logout: async () => await api.post(getAuthUrl(requestUrls.logout)),
  requestPasswordReset: async (email: string) =>
    await api.post(
      `${getAuthUrl(requestUrls.requestPasswordReset)}?email=${email}`
    ),
  resetPassword: async (token: string, new_password: string) =>
    await api.post(
      `${getAuthUrl(
        requestUrls.resetPassword
      )}/${token}?new_password=${new_password}`
    ),
  getToken: async () => await api.get(getAuthUrl(requestUrls.getToken)),
  refreshToken: async () =>
    await api.post(getAuthUrl(requestUrls.refreshToken)),
};
