import React from "react";
import { Flex, Spin } from "antd";

const containerStyle: React.CSSProperties = {
  marginTop: 200,
};

const Loader: React.FC = () => (
  <Flex justify="center" align="center" style={containerStyle}>
    <Spin size="large" />
  </Flex>
);

export default Loader;
