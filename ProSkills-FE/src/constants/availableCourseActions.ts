import { studentApi } from "../api/students";
import {
  CourseActions,
  CoursePage,
  UserAvailableCourseActions,
  UserAvailableCourseActionsByPage,
} from "../models/Course";
import { GUEST_ROLE, UserRoles } from "../models/User";
import { PATHS } from "../routes/paths";
import { handleAxiosRequest } from "../utils/axiosUtils";
import { getUserAvailableCourseActionsByPage } from "../utils/courseUtils";
import { EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { ReactNode } from "react";

export const courseActions: CourseActions = {
  more: {
    title: "More...",
    link: PATHS.COURSE.link,
    dynamicParam: {
      stringToReplace: ":courseId",
      propName: "id",
    },
    visible: {
      [CoursePage.AllCourses]: true,
      [CoursePage.MyCourses]: true,
      [CoursePage.CourseDetails]: false,
    },
  },
  enroll: {
    title: "Enroll",
    link: "",
    visible: {
      [CoursePage.AllCourses]: true,
      [CoursePage.MyCourses]: false,
      [CoursePage.CourseDetails]: false,
    },
    buttonProps: {
      type: "primary",
      disabled: true,
    },
    onClick: async (courseId, notification) => {
      return await handleAxiosRequest(
        () => studentApi.enrollToCourse(courseId),
        notification,
        'Congrats, you\'ve enrolled the course! You can see it in "My Courses" section.'
      );
    },
    disabledIfAlreadyEnrolled: true,
  },
  edit: {
    title: "Edit",
    icon: EditOutlined,
    link: `${PATHS.COURSE.link}/${PATHS.EDIT_COURSE.link}`,
    dynamicParam: {
      stringToReplace: ":courseId",
      propName: "id",
    },
    visible: {
      [CoursePage.AllCourses]: false,
      [CoursePage.MyCourses]: true,
      [CoursePage.CourseDetails]: false,
    },
    buttonProps: {
      type: "dashed",
    },
  },
  delete: {
    title: "Delete",
    icon: DeleteOutlined,
    link: "",
    dynamicParam: {
      stringToReplace: ":courseId",
      propName: "id",
    },
    visible: {
      [CoursePage.AllCourses]: false,
      [CoursePage.MyCourses]: true,
      [CoursePage.CourseDetails]: false,
    },
    buttonProps: {
      type: "dashed",
    },
  },
  assignments: {
    title: "Assignments",
    link: PATHS.COURSE_SECTIONS.link,
    dynamicParam: {
      stringToReplace: ":courseId",
      propName: "id",
    },
    visible: {
      [CoursePage.AllCourses]: false,
      [CoursePage.MyCourses]: true,
      [CoursePage.CourseDetails]: false,
    },
  },
  rate: {
    title: "Rate",
    link: PATHS.COURSE_RATE.link,
    dynamicParam: {
      stringToReplace: ":courseId",
      propName: "id",
    },
    visible: {
      [CoursePage.AllCourses]: false,
      [CoursePage.MyCourses]: true,
      [CoursePage.CourseDetails]: false,
    },
    buttonProps: {
      type: "dashed",
    },
  },
};

export const userAvailableCourseActions: UserAvailableCourseActions = {
  [UserRoles.STUDENT]: [
    courseActions.enroll,
    courseActions.assignments,
    courseActions.more,
  ],
  [UserRoles.TEACHER]: [
    courseActions.edit,
    courseActions.delete,
    courseActions.assignments,
    courseActions.more,
  ],
  [GUEST_ROLE]: [courseActions.more],
  [UserRoles.ADMIN]: [courseActions.more],
};

// each page should include only actions which should be visible on that page
export const userAvailableCourseActionsByPage: UserAvailableCourseActionsByPage =
  Object.fromEntries(
    Object.values(CoursePage).map((page) => [
      page,
      getUserAvailableCourseActionsByPage(page as CoursePage),
    ])
  ) as UserAvailableCourseActionsByPage;
