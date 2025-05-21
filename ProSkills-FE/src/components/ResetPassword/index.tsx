import React from "react";
import { Form, Input, notification } from "antd";
import { useNavigate, useParams } from "react-router";
import { authApi } from "../../api/auth";
import ResetPasswordForm from "../ResetPasswordForm";
import { PATHS } from "../../routes/paths";
import axios from "axios";
import { useAuthStore } from "../../store/useAuthStore";

const ResetPassword: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useParams<{ token: string }>();

  const onFinish = async (values: {
    new_password: string;
    confirm: string;
  }) => {
    try {
      await authApi.resetPassword(token!, values.new_password);
      notification.success({
        message: "Password Reset Successful",
        description:
          "Your password has been reset successfully. Please login with your new password.",
      });

      useAuthStore.getState().resetLoginAttempts();

      navigate(PATHS.AUTH.link);
    } catch (error) {
      let errorDescription =
        "There was an error resetting your password. Please try again.";

      if (axios.isAxiosError(error)) {
        errorDescription = error.response?.data?.detail;
      }

      notification.error({
        message: "Password Reset Failed",
        description: errorDescription,
      });
    }
  };

  return (
    <ResetPasswordForm onFinish={onFinish}>
      <Form.Item
        label="New Password"
        name="new_password"
        validateFirst
        rules={[
          { required: true, message: "Please input your password!" },
          { min: 8, message: "Password must have at least 8 characters!" },
          {
            pattern: /[A-Z]/,
            message: "Password must include an uppercase letter",
          },
          {
            pattern: /\d/,
            message: "Password must have at least 1 digit!",
          },
        ]}
        hasFeedback
      >
        <Input.Password placeholder="Enter new password" />
      </Form.Item>
      <Form.Item
        label="Confirm New Password"
        name="confirm"
        dependencies={["new_password"]}
        hasFeedback
        rules={[
          { required: true, message: "Please confirm your new password!" },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue("new_password") === value) {
                return Promise.resolve();
              }
              return Promise.reject(
                new Error("The two passwords do not match!")
              );
            },
          }),
        ]}
      >
        <Input.Password placeholder="Confirm new password" />
      </Form.Item>
    </ResetPasswordForm>
  );
};

export default ResetPassword;
