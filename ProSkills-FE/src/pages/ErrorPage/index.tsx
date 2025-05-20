import React from "react";
import { Flex, Empty, Typography } from "antd";

const ErrorPage: React.FC = () => {
  return (
    <Flex style={{ marginTop: 100 }} justify="center">
      <Empty
        description={
          <Typography.Text>Oops! This page doesn't exist.</Typography.Text>
        }
      ></Empty>
    </Flex>
  );
};

export default ErrorPage;
