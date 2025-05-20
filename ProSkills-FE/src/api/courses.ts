import api from ".";
import { PostCourse } from "../models/Course";

const COURSES_BASE_URL = "/courses";

export const coursesApi = {
  getAll: async () => api.get(COURSES_BASE_URL),
  getById: async (courseId: string) =>
    api.get(`${COURSES_BASE_URL}/${courseId}`),
  create: async (body: PostCourse) => await api.post(COURSES_BASE_URL, body),
  update: async (courseId: string, body: PostCourse) =>
    await api.put(`${COURSES_BASE_URL}/${courseId}`, body),
  delete: async (courseId: string) =>
    await api.delete(`${COURSES_BASE_URL}/${courseId}`),
  rate: async (courseId: string, rating: number) =>
    await api.post(`${COURSES_BASE_URL}/${courseId}/rate`, { rating }),
};
