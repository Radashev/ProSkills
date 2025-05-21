import React from "react";
import { Outlet } from "react-router";
import { Layout, theme } from "antd";
import Header from "../../components/Header";
import classes from "./RootLayout.module.css";

const { Content, Footer } = Layout;

const RootLayout: React.FC = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <Layout className={classes.layout}>
      <Header />
      <Content className={classes.content}>
        <div
          className={classes.outletWrapper}
          style={{
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Outlet />
        </div>
      </Content>
      <Footer className={classes.footer}>
        ProSkills ©{new Date().getFullYear()} Created by Team №1 (THE GAME
        EDUCATION)
      </Footer>
    </Layout>
  );
};

export default RootLayout;
