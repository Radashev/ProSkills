import React from "react";
import { useLoaderData, useNavigation } from "react-router";
import CoursesList from "../../components/CoursesList";
import Loader from "../../components/Loader";
import { coursesApi } from "../../api/courses";
import { GetCourse } from "../../models/Course";

const AllCourses: React.FC = () => {
  const courses = useLoaderData();
  const navigation = useNavigation();

  if (navigation.state === "loading") {
    return <Loader />;
  }

  return <CoursesList courses={courses} />;
};

export default AllCourses;

export async function loader() {
  const response = await coursesApi.getAll();

  if (response.status === 200) {
    return response.data
      .map((el: GetCourse) => ({
        ...el,
        key: el.id,
      }))
      .sort((a: GetCourse, b: GetCourse) => b.rating - a.rating);
  }

  return [];
}
