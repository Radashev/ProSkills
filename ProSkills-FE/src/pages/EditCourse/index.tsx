import { useRouteLoaderData } from "react-router";
import CourseForm from "../../components/CourseForm";
import { GetCourse } from "../../models/Course";

const EditCoursePage: React.FC = () => {
  const { course } = useRouteLoaderData("courseDetails");

return <CourseForm course={course} />;
};

export default EditCoursePage;
