import React from "react";
import { Form, Button, Typography, Flex, theme } from "antd";
import classes from "./ResetPasswordForm.module.css";
import { ResetPasswordFormProps } from "../../models/Auth";
import GoBackButton from "../GoBackButton";

const { Title } = Typography;

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  onFinish,
  children,
  ...props
}) => {
  const [form] = Form.useForm();
  const { token: themeToken } = theme.useToken();

  return (
    <Flex
      vertical
      justify="center"
      align="center"
      className={classes.resetPassContainer}
    >
      <Title level={2} style={{ color: themeToken.colorPrimary }}>
        Reset Your Password
      </Title>
      <Flex vertical align="center" className={classes.formWrapper}>
        <Form form={form} layout="vertical" onFinish={onFinish} {...props}>
          {children}
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Submit
            </Button>
          </Form.Item>
        </Form>
        <Flex justify="center" align="center" gap={10}>
          or <GoBackButton />
        </Flex>
      </Flex>
    </Flex>
  );
};

export default ResetPasswordForm;
