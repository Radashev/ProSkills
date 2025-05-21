import React, { JSX } from "react";
import { Button, Form, Input } from "antd";
import AuthForm from "../AuthForm";
import { formItemsLayouts } from "./formItemsLayouts";
import { UserRoles } from "../../models/User";
import { formInputs } from "../../constants/formInputs";

const Register: React.FC<{ userRoleToCreate?: UserRoles }> = ({
  userRoleToCreate = UserRoles.STUDENT,
}) => {
  const inputKeys = [
    "registerEmail",
    "first_name",
    "last_name",
    "registerPassword",
    "confirmPassword",
  ];
  const inputs = formInputs.filter(
    (el: JSX.Element) =>
      typeof el.key === "string" && inputKeys.includes(el.key)
  );

  return (
    <AuthForm
      mode="register"
      name="register"
      userRoleToCreate={userRoleToCreate}
      scrollToFirstError
      {...formItemsLayouts.formItem}
    >
      {() => (
        <>
          {inputs.map((el) => el)}

          <Form.Item
            {...(userRoleToCreate === UserRoles.STUDENT
              ? formItemsLayouts.registerButton
              : {})}
          >
            <Button type="primary" htmlType="submit">
              Register
            </Button>
          </Form.Item>
        </>
      )}
    </AuthForm>
  );
};

export default Register;
