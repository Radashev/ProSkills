export const GUEST_ROLE = "guest" as const;

export enum UserRoles {
  STUDENT = "student",
  TEACHER = "teacher",
  ADMIN = "admin",
}

export interface UserRegistration {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRoles.STUDENT;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  email: string;
  role: UserRoles;
}
