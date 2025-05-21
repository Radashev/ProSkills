import { MenuProps } from "antd";
import { HomeOutlined, LoginOutlined, LogoutOutlined } from "@ant-design/icons";
import { UserRoles } from "../models/User";
import { PATHS, ROLE_PATHS } from "../routes/paths";
import classes from "../components/Header/Header.module.css";

export type MenuItem = Required<MenuProps>["items"][number];

type UserAvailableHeaderTabs = {
  [role: string]: MenuItem[];
};

export const headerTabs = [
  {
    key: PATHS.HOME.link,
    label: "Home",
    icon: <HomeOutlined />,
  },
  {
    key: PATHS.COURSES.link,
    label: "All Courses",
  },
  {
    key: PATHS.MY_COURSES.link,
    label: "My Courses",
  },
  {
    key: PATHS.STUDENTS.link,
    label: "Students",
  },
  {
    key: PATHS.LOGOUT.link,
    label: "Log out",
    icon: <LogoutOutlined />,
    className: classes.menuLastItem,
  },
  {
    key: PATHS.AUTH.link,
    label: "Login",
    icon: <LoginOutlined />,
    className: classes.menuLastItem,
  },
];

export const availableHeaderTabs: UserAvailableHeaderTabs = {};

for (const role in ROLE_PATHS) {
  const userRole = role as UserRoles;
  const paths = ROLE_PATHS[userRole];

  const tabs = headerTabs.filter((tab) => paths.includes(tab.key));

  availableHeaderTabs[role] = tabs;
}
