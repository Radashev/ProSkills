import { Form, Input } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { JSX } from "react";

export const formInputs: JSX.Element[] = [
  <Form.Item
    key="email"
    name="email"
    rules={[
      { type: "email", message: "The input is not valid Email!" },
      { required: true, message: "Please input your Email!" },
    ]}
  >
    <Input prefix={<UserOutlined />} placeholder="Email" />
  </Form.Item>,

  <Form.Item
    key="loginPassword"
    name="password"
    rules={[{ required: true, message: "Please input your Password!" }]}
  >
    <Input.Password
      prefix={<LockOutlined />}
      type="password"
      placeholder="Password"
    />
  </Form.Item>,

  <Form.Item
    key="registerEmail"
    name="email"
    label="Email"
    rules={[
      { type: "email", message: "The input is not valid Email!" },
      { required: true, message: "Please input your Email!" },
    ]}
  >
    <Input />
  </Form.Item>,

  <Form.Item
    key="first_name"
    name="first_name"
    label="First Name"
    rules={[
      { required: true, message: "Please input the first name!" },
      { pattern: /^\S+$/, message: "Spaces are not allowed" },
    ]}
  >
    <Input />
  </Form.Item>,

  <Form.Item
    key="last_name"
    name="last_name"
    label="Last Name"
    rules={[
      { required: true, message: "Please input the last name!" },
      { pattern: /^\S+$/, message: "Spaces are not allowed" },
    ]}
  >
    <Input />
  </Form.Item>,

  <Form.Item
    key="registerPassword"
    name="password"
    label="Password"
    validateFirst
    rules={[
      { required: true, message: "Please input your password!" },
      { pattern: /^\S+$/, message: "Spaces are not allowed" },
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
    <Input.Password />
  </Form.Item>,

  <Form.Item
    key="confirmPassword"
    name="confirm"
    label="Confirm Password"
    dependencies={["password"]}
    hasFeedback
    validateFirst
    rules={[
      { required: true, message: "Please confirm your password!" },
      { pattern: /^\S+$/, message: "Spaces are not allowed" },
      ({ getFieldValue }) => ({
        validator(_, value) {
          if (!value || getFieldValue("password") === value) {
            return Promise.resolve();
          }
          return Promise.reject(new Error("Passwords do not match!"));
        },
      }),
    ]}
  >
    <Input.Password />
  </Form.Item>,
];
