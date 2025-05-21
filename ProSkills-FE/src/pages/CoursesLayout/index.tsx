import { Flex } from "antd";
import { Outlet, useLocation } from "react-router";
import GoBackButton from "../../components/GoBackButton";
import { PATHS } from "../../routes/paths";

const CoursesLayout: React.FC = () => {
  const location = useLocation();
  const isCoursesPage =
    location.pathname === PATHS.COURSES.link ||
    location.pathname === PATHS.MY_COURSES.link;

  return (
    <Flex vertical gap={5} style={{ height: "100%" }}>
      {!isCoursesPage && <GoBackButton />}
      <Outlet />
    </Flex>
  );
};

export default CoursesLayout;
