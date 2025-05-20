import { Flex } from "antd";
import { Tabs } from "antd";
import StudentsList from "../../components/StudentsList";
import classes from "./StudentsPage.module.css";
import { useAuthStore } from "../../store/useAuthStore";
import { studentApi } from "../../api/students";
import { GetCourse } from "../../models/Course";
import { useLoaderData } from "react-router";
import TitleComp from "../../components/Title";

// Cache for the loader data
let cachedCourses: GetCourse[] | null = null;

const StudentsPage: React.FC = () => {
  const teacherCourses = useLoaderData();

  return (
    <Flex vertical align="center" gap={20}>
      <TitleComp>Students</TitleComp>
      <Flex justify="center">
        {teacherCourses.length ? (
          <Tabs
            defaultActiveKey="1"
            tabPosition="top"
            className={classes.tabs}
            type="card"
            items={teacherCourses.map((course: GetCourse) => ({
              label: course.title,
              key: course.id,
              children: <StudentsList courseId={course.id + ""} />,
            }))}
          />
        ) : (
          <Flex justify="center" style={{ width: "100%" }}>
            There're no courses yet
          </Flex>
        )}
      </Flex>
    </Flex>
  );
};

export default StudentsPage;

export async function loader() {
  if (cachedCourses) {
    return cachedCourses;
  }

  const { checkAuth } = useAuthStore.getState();
  await checkAuth();

  const response = await studentApi.getTeacherCourses();

  if (response.status === 200) {
    cachedCourses = response.data.map((el: GetCourse) => ({
      ...el,
      key: el.id,
    }));
    return cachedCourses;
  }

  return [];
}
