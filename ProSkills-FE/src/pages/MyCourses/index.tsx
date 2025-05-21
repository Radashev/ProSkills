import { useLoaderData, useNavigation } from "react-router";
import { CoursePage, GetCourse } from "../../models/Course";
import CoursesList from "../../components/CoursesList";
import { useAuthStore } from "../../store/useAuthStore";
import { studentApi } from "../../api/students";
import { UserRoles } from "../../models/User";
import Loader from "../../components/Loader";

const MyCourses: React.FC = () => {
  const courses = useLoaderData();
  const navigation = useNavigation();

  if (navigation.state === "loading") {
    return <Loader />;
  }

  return <CoursesList courses={courses} mode={CoursePage.MyCourses} />;
};

export default MyCourses;

export async function loader() {
  const { user } = useAuthStore.getState();
  if (!user) return [];

  const response = await studentApi[
    user.role === UserRoles.TEACHER ? "getTeacherCourses" : "getStudentCourses"
  ]();

  if (response.status === 200) {
    const courses = response.data
      .map((el: GetCourse) => ({
        ...el,
        key: el.id,
      }))
      .sort((a: GetCourse, b: GetCourse) => b.rating - a.rating);
    return courses;
  }

  return [];
}
