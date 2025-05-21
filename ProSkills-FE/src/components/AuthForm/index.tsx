import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { AxiosError, AxiosResponse } from "axios";
import {
  Typography,
  Flex,
  Form,
  theme,
  notification as antdNotification,
} from "antd";
import { handleAuthResponse } from "../../utils/authUtils";
import { capitalizeFirstLetter } from "../../utils/stringUtils";
import {
  LoginFormData,
  RegisterFormData,
  AuthRequestType,
  AuthFormProps,
} from "../../models/Auth";
import { APIError } from "../../models/APIResponse";
import { authApi } from "../../api/auth";
import logo from "../../assets/logo.png";
import classes from "./AuthForm.module.css";
import { UserRoles } from "../../models/User";
import { PATHS } from "../../routes/paths";
import { useAuthStore } from "../../store/useAuthStore";

const TIME_TO_PREVENT_LOGIN_MS = 10 * 60 * 1000;

const AuthForm: React.FC<AuthFormProps> = ({
  mode,
  userRoleToCreate = UserRoles.STUDENT,
  children,
  ...props
}) => {
  const [notification, contextHolder] = antdNotification.useNotification();
  const navigate = useNavigate();
  const { token: themeToken } = theme.useToken();
  const { Title, Paragraph } = Typography;

  const { loginAttempts, resetLoginAttempts } = useAuthStore();
  const failedLogin = mode === "login" && loginAttempts >= 5;

  const [remainingTime, setRemainingTime] = useState<number>(0);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval> | undefined;

    if (failedLogin) {
      let disabledUntilStr = localStorage.getItem("disabledUntil");
      let disabledUntil: number;

      if (!disabledUntilStr) {
        disabledUntil = Date.now() + TIME_TO_PREVENT_LOGIN_MS;
        localStorage.setItem("disabledUntil", disabledUntil.toString());
      } else {
        disabledUntil = Number(disabledUntilStr);
      }

      // calculate initial remaining time
      const initialRemaining = Math.max(
        0,
        Math.floor((disabledUntil - Date.now()) / 1000)
      );
      setRemainingTime(initialRemaining);

      intervalId = setInterval(() => {
        const now = Date.now();
        const diff = Math.max(0, Math.floor((disabledUntil - now) / 1000));
        setRemainingTime(diff);

        if (diff <= 0) {
          clearInterval(intervalId!);
          localStorage.removeItem("disabledUntil");
          resetLoginAttempts();
        }
      }, 1000);
    } else {
      localStorage.removeItem("disabledUntil");
      setRemainingTime(0);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [failedLogin, resetLoginAttempts]);

  const modeToNavigate: AuthRequestType =
    mode === "login" ? "register" : "login";
  const navigateMessage: string =
    modeToNavigate === "login"
      ? "Already have an account?"
      : "Don't have an account?";
  const isStudentRegistration = userRoleToCreate === UserRoles.STUDENT;

  const onFinish = async (formData: RegisterFormData | LoginFormData) => {
    const response: AxiosResponse | AxiosError<APIError> =
      mode === "register"
        ? await authApi.register(formData as RegisterFormData, userRoleToCreate)
        : await authApi.login(formData as LoginFormData);

    await handleAuthResponse(
      response,
      mode,
      userRoleToCreate,
      notification,
      navigate
    );
  };

  const minutes = Math.floor(remainingTime / 60);
  const seconds = remainingTime % 60;

  return (
    <Flex
      vertical
      justify="center"
      align="center"
      className={isStudentRegistration ? classes.authContainer : ""}
    >
      <Flex justify="center" align="center">
        <img className={classes.logo} src={logo} alt="Logo" />
        <Title style={{ color: themeToken.colorPrimary }}>ProSkills</Title>
      </Flex>
      <Flex vertical align="center" className={classes.formWrapper}>
        <Form onFinish={onFinish} {...props}>
          {children(failedLogin)}
          {contextHolder}
        </Form>
        {failedLogin && (
          <>
            <Paragraph
              style={{ textAlign: "center", color: "red", maxWidth: "15rem" }}
            >
              Too many failed login attempts.
            </Paragraph>
            <Paragraph style={{ textAlign: "center" }}>
              <span style={{ color: "black" }}>Please </span>
              <Link
                to={PATHS.REQUEST_PASSWORD_RESET.link}
                className="underline"
              >
                reset your password
              </Link>{" "}
              <span style={{ color: "black" }}>
                or try to login again in {minutes}m{" "}
                {seconds < 10 ? `0${seconds}` : seconds}s.
              </span>
            </Paragraph>
          </>
        )}
        <Paragraph>
          {navigateMessage}{" "}
          <Link to={`?mode=${modeToNavigate}`}>
            {capitalizeFirstLetter(modeToNavigate)}
          </Link>
        </Paragraph>
      </Flex>
    </Flex>
  );
};

export default AuthForm;
