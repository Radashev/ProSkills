import { Flex } from "antd";
import { Outlet, useLocation } from "react-router";
import GoBackButton from "../../components/GoBackButton";
import { PATHS } from "../../routes/paths";

const StudentsLayout: React.FC = () => {
  const location = useLocation();
  const isStudentsPage = location.pathname === PATHS.STUDENTS.link;

  return (
    <Flex vertical gap={5} style={{ height: "100%" }}>
      {!isStudentsPage && <GoBackButton />}
      <Outlet />
    </Flex>
  );
};

export default StudentsLayout;
