import React, { JSX } from "react";
import { Button, Form, Flex } from "antd";
import AuthForm from "../AuthForm";
import { formInputs } from "../../constants/formInputs";

const Login: React.FC = () => {
  const inputKeys = ["email", "loginPassword"];
  const inputs = formInputs.filter(
    (el: JSX.Element) =>
      typeof el.key === "string" && inputKeys.includes(el.key)
  );

  return (
    <AuthForm mode="login" name="login">
      {(disableSubmit) => (
        <>
          {inputs.map((el) => el)}
          <Form.Item>
            <Flex vertical align="center" gap={20}>
              <Button
                block
                type="primary"
                htmlType="submit"
                disabled={disableSubmit}
              >
                Log in
              </Button>
            </Flex>
          </Form.Item>
        </>
      )}
    </AuthForm>
  );
};

export default Login;
