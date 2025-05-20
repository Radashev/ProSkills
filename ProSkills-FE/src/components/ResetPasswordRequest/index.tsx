import React, { JSX, useState } from "react";
import { Form, Input, notification, theme } from "antd";
import { useNavigate } from "react-router";
import { authApi } from "../../api/auth";
import { PATHS } from "../../routes/paths";
import ResetPasswordForm from "../ResetPasswordForm";
import { formInputs } from "../../constants/formInputs";
import { AxiosError } from "axios";
import { APIError } from "../../models/APIResponse";
import Loader from "../Loader";

const ResetPasswordRequest: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);

  const inputKeys = ["email"];
  const inputs = formInputs.filter(
    (el: JSX.Element) =>
      typeof el.key === "string" && inputKeys.includes(el.key)
  );

  const onFinish = async (values: { email: string }) => {
    setLoading(true);

    try {
      await authApi.requestPasswordReset(values.email);
      notification.success({
        message: "Password Reset Requested",
        description: "Please check your email for reset instructions.",
      });

      setLoading(false);
      navigate(PATHS.AUTH.link);
    } catch (error: AxiosError<APIError> | any) {
      setLoading(false);
      notification.error({
        message: "Reset Request Failed",
        description:
          error.response.data.detail ||
          "There was a problem sending your reset request. Please try again later.",
      });
    }
  };

  return (
    <>
      {loading ? (
        <Loader />
      ) : (
        <ResetPasswordForm onFinish={onFinish}>
          {inputs.map((el) => el)}
        </ResetPasswordForm>
      )}
    </>
  );
};

export default ResetPasswordRequest;
