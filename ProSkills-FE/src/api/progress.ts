import api from ".";
import { PostAssignmentGrade } from "../models/Course";
const PROGRESS_BASE_URL = "/progress";

export const progressApi = {
  getByCourse: async (courseId: string, studentId: string) =>
    await api.get(
      `${PROGRESS_BASE_URL}/courses/${courseId}/student/${studentId}`
    ),
  markAsDone: async (assignmentId: string) =>
    await api.post(
      `${PROGRESS_BASE_URL}/mark-assignment-complete/${assignmentId}`
    ),
  markAsDoneWithFile: async (assignmentId: string, file: FormData) =>
    await api.post(`/file-storage/assignments/${assignmentId}/submit`, file, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }),
  gradeAssignment: async (
    assignmentId: string,
    studentId: string,
    body: PostAssignmentGrade
  ) =>
    await api.post(
      `${PROGRESS_BASE_URL}/assignments/${assignmentId}/student/${studentId}/grade`,
      body
    ),
};
