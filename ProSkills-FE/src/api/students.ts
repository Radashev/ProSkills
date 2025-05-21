import api from ".";

const STUDENT_BASE_URL = "/students";

export const studentApi = {
  getAllStudentsByCourse: async (courseId: string) =>
    await api.get(`${STUDENT_BASE_URL}/teaching/courses/${courseId}/students`),
  getStudentCourses: async () =>
    await api.get(`${STUDENT_BASE_URL}/enrollments/courses`),
  getTeacherCourses: async () =>
    await api.get(`${STUDENT_BASE_URL}/teaching/courses`),
  enrollToCourse: async (courseId: string) =>
    await api.post(`${STUDENT_BASE_URL}/enrollments/courses/${courseId}`),
  deleteFromCourse: async (studentId: string, courseId: string) =>
    await api.delete(
      `${STUDENT_BASE_URL}/enrollments/courses/${courseId}/students/${studentId}`
    ),
};
