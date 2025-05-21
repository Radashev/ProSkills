import { Flex, Typography } from "antd";
import { Link } from "react-router";
import { PATHS } from "../../routes/paths";
import TitleComp from "../../components/Title";

const Home: React.FC = () => {
  return (
    <Flex vertical justify="center" align="center">
      <TitleComp>ProSkills Home Page</TitleComp>
      <Typography.Paragraph>
        Check out the new courses in{" "}
        {<Link to={PATHS.COURSES.link}>All Courses</Link>} section!
      </Typography.Paragraph>
    </Flex>
  );
};

export default Home;
