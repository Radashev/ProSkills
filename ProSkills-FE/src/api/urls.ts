export const urls = {
  auth: {
    register: {
      student: "/users",
      teacher: "/register/teacher",
      admin: "/users/admin",
    },
    login: "/token",
    logout: "/logout",
    requestPasswordReset: "/reset-password",
    resetPassword: "/reset-password",
    getToken: "/me",
    refreshToken: "/refresh",
  },
};
