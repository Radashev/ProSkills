import React from "react";
import { Link, useNavigate, useSubmit, useLocation } from "react-router";
import { PATHS, ROLE_PATHS } from "../../routes/paths";
import { Layout, Menu, MenuProps, theme } from "antd";
import { HomeOutlined, LoginOutlined, LogoutOutlined } from "@ant-design/icons";
import classes from "./Header.module.css";
import logo from "../../assets/logo.png";
import { useAuthStore } from "../../store/useAuthStore";
import { GUEST_ROLE, UserRoles } from "../../models/User";
import {
  availableHeaderTabs,
  MenuItem,
} from "../../constants/availableHeaderTabs";

const { Header: AntHeader } = Layout;

const Header: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const submit = useSubmit();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const role = useAuthStore((state) => state.user?.role) || GUEST_ROLE;
  const menuItems: MenuItem[] = availableHeaderTabs[role];
  const selectedKey = location.pathname;

  const handleMenuItemClick = ({ key }: { key: string }) => {
    if (key === PATHS.LOGOUT.link) {
      submit(null, { action: PATHS.LOGOUT.link, method: "POST" });
    } else if (key) {
      navigate(key);
    }
  };

  return (
    <AntHeader
      className={classes.header}
      style={{ background: colorBgContainer }}
    >
      <Link to={PATHS.HOME.link} className={classes.logoWrapper}>
        <img src={logo} className={classes.logo} alt="Logo" />
      </Link>
      <Menu
        className={classes.menu}
        mode="horizontal"
        items={menuItems}
        selectedKeys={[selectedKey]}
        onClick={handleMenuItemClick}
      />
    </AntHeader>
  );
};

export default Header;