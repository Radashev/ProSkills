import { PATHS } from "./paths";
import Home from "../pages/Home";
import AuthPage from "../pages/AuthPage";
import ErrorPage from "../pages/ErrorPage";
import { rootLoader } from "../utils/authUtils";
import { action as logoutAction } from "../pages/Logout";
import RootLayout from "../pages/RootLayout";
import Loader from "../components/Loader";
import ProtectedRoute from "../components/ProtectedRoute";
import AllCourses, { loader as allCoursesLoader } from "../pages/AllCourses";
import CourseDetails, {
  loader as courseDetailsLoader,
} from "../pages/CourseDetails";
import NewCoursePage from "../pages/NewCourse";
import CoursesLayout from "../pages/CoursesLayout";
import EditCoursePage from "../pages/EditCourse";
import MyCourses, { loader as myCoursesLoader } from "../pages/MyCourses";
import DeleteCoursePage, {
  action as deleteCourseAction,
} from "../pages/DeleteCourse";
import StudentsPage, {
  loader as studentsPageLoader,
} from "../pages/StudentsPage";
import ResetPasswordRequest from "../components/ResetPasswordRequest";
import ResetPassword from "../components/ResetPassword";
import CourseSections, {
  loader as courseSectionsLoader,
} from "../pages/CourseSections";
import AssignmentsForReview, {
  loader as assignmentsForReviewLoader,
} from "../pages/AssignmentsForReview";
import StudentsLayout from "../pages/StudentsLayout";

export const routes = [
  {
    id: "root",
    path: PATHS.HOME.link,
    element: <RootLayout />,
    loader: rootLoader,
    HydrateFallback: Loader,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        id: "coursesRoot",
        path: PATHS.COURSES.link,
        element: <CoursesLayout />,
        children: [
          {
            index: true,
            element: (
              <ProtectedRoute allowedRoles={[...PATHS.COURSES.roles]}>
                <AllCourses />
              </ProtectedRoute>
            ),
            loader: allCoursesLoader,
          },
          {
            path: PATHS.MY_COURSES.link,
            element: (
              <ProtectedRoute allowedRoles={[...PATHS.MY_COURSES.roles]}>
                <MyCourses />
              </ProtectedRoute>
            ),
            loader: myCoursesLoader,
          },
          {
            id: "courseDetails",
            path: PATHS.COURSE.link,
            loader: courseDetailsLoader,
            children: [
              {
                index: true,
                element: (
                  <ProtectedRoute allowedRoles={[...PATHS.COURSE.roles]}>
                    <CourseDetails />
                  </ProtectedRoute>
                ),
              },
              {
                path: PATHS.EDIT_COURSE.link,
                element: (
                  <ProtectedRoute allowedRoles={[...PATHS.EDIT_COURSE.roles]}>
                    <EditCoursePage />
                  </ProtectedRoute>
                ),
              },
              {
                path: PATHS.DELETE_COURSE.link,
                element: (
                  <ProtectedRoute allowedRoles={[...PATHS.DELETE_COURSE.roles]}>
                    <DeleteCoursePage />
                  </ProtectedRoute>
                ),
                action: deleteCourseAction,
              },
              {
                path: PATHS.COURSE_SECTIONS.link,
                element: (
                  <ProtectedRoute
                    allowedRoles={[...PATHS.COURSE_SECTIONS.roles]}
                  >
                    <CourseSections />
                  </ProtectedRoute>
                ),
                loader: courseSectionsLoader,
              },
            ],
          },
          {
            path: PATHS.NEW_COURSE.link,
            element: (
              <ProtectedRoute allowedRoles={[...PATHS.NEW_COURSE.roles]}>
                <NewCoursePage />
              </ProtectedRoute>
            ),
          },
        ],
      },
      {
        id: "studentsRoot",
        path: PATHS.STUDENTS.link,
        element: <StudentsLayout />,
        children: [
          {
            index: true,
            element: (
              <ProtectedRoute allowedRoles={[...PATHS.STUDENTS.roles]}>
                <StudentsPage />
              </ProtectedRoute>
            ),
            loader: studentsPageLoader,
          },
        ],
      },
      {
        path: PATHS.STUDENT_ASSIGNMENTS_FOR_REVIEW.link,
        element: (
          <ProtectedRoute
            allowedRoles={[...PATHS.STUDENT_ASSIGNMENTS_FOR_REVIEW.roles]}
          >
            <AssignmentsForReview />
          </ProtectedRoute>
        ),
        loader: assignmentsForReviewLoader,
      },
      {
        path: PATHS.LOGOUT.link,
        element: <ProtectedRoute allowedRoles={[...PATHS.LOGOUT.roles]} />,
        children: [{ index: true }],
        action: logoutAction,
      },
      {
        path: PATHS.NOT_FOUND.link,
        element: <ErrorPage />,
      },
    ],
  },
  {
    path: PATHS.AUTH.link,
    element: <ProtectedRoute allowedRoles={[...PATHS.AUTH.roles]} />,
    children: [{ index: true, element: <AuthPage /> }],
  },
  {
    path: PATHS.REQUEST_PASSWORD_RESET.link,
    element: (
      <ProtectedRoute allowedRoles={[...PATHS.REQUEST_PASSWORD_RESET.roles]}>
        <ResetPasswordRequest />
      </ProtectedRoute>
    ),
  },
  {
    path: PATHS.RESET_PASSWORD.link,
    element: (
      <ProtectedRoute allowedRoles={[...PATHS.RESET_PASSWORD.roles]}>
        <ResetPassword />
      </ProtectedRoute>
    ),
  },
];
