import { FormProps } from "antd";
import { UserRoles } from "./User";

export type AuthRequestType = "register" | "login";

export interface RegisterFormData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface AuthFormProps extends Omit<FormProps, "children"> {
  mode: AuthRequestType;
  userRoleToCreate?: UserRoles;
  children: (disableSubmit: boolean) => React.ReactNode;
}

export interface ResetPasswordFormProps<T = Record<string, any>>
  extends FormProps {
  onFinish: (values: any) => void;
  children: React.ReactNode;
}
