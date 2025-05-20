import { GUEST_ROLE, UserRoles } from "../models/User";

export const PATHS = {
  HOME: {
    link: "/",
    roles: [...Object.values(UserRoles), GUEST_ROLE],
  },
  AUTH: {
    link: "/auth",
    roles: [GUEST_ROLE],
  },
  REQUEST_PASSWORD_RESET: {
    link: "/request-password-reset",
    roles: [GUEST_ROLE],
  },
  RESET_PASSWORD: {
    link: "/reset-password/:token",
    roles: [GUEST_ROLE],
  },
  COURSES: {
    link: "/courses",
    roles: [...Object.values(UserRoles), GUEST_ROLE],
  },
  MY_COURSES: {
    link: "/courses/my",
    roles: [UserRoles.TEACHER, UserRoles.STUDENT],
  },
  COURSE: {
    link: "/courses/:courseId",
    roles: [...Object.values(UserRoles), GUEST_ROLE],
  },
  EDIT_COURSE: {
    link: "edit",
    roles: [UserRoles.TEACHER],
  },
  DELETE_COURSE: {
    link: "delete",
    roles: [UserRoles.TEACHER],
  },
  NEW_COURSE: {
    link: "/courses/my/new",
    roles: [UserRoles.TEACHER],
  },
  COURSE_SECTIONS: {
    link: "/courses/:courseId/sections",
    roles: [UserRoles.TEACHER, UserRoles.STUDENT],
  },
  COURSE_RATE: {
    link: "/courses/:courseId/rate",
    roles: [UserRoles.STUDENT],
  },
  STUDENTS: {
    link: "/students",
    roles: [UserRoles.TEACHER],
  },
  STUDENT_ASSIGNMENTS_FOR_REVIEW: {
    link: "/assignments-review",
    roles: [UserRoles.TEACHER],
  },
  LOGOUT: {
    link: "logout",
    roles: Object.values(UserRoles),
  },
  NOT_FOUND: {
    link: "*",
    roles: [],
  },
} as const;

export const ROLE_PATHS = Object.entries(PATHS).reduce(
  (acc, [pathName, { link, roles }]) => {
    roles.forEach((role) => {
      if (!acc[role]) {
        acc[role] = [];
      }
      acc[role].push(link);
    });
    return acc;
  },
  {} as Record<string, string[]>
);
