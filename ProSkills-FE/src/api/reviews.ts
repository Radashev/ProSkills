import api from ".";
import { PostCourseReview } from "../models/Course";

const REVIEWS_BASE_URL = "/reviews";

export const reviewsApi = {
  getAllByUserId: async (userId: string) =>
    api.get(`${REVIEWS_BASE_URL}/users/${userId}`),
  getByCourseId: async (courseId: string) =>
    await api.get(`${REVIEWS_BASE_URL}/courses/${courseId}`),
  create: async (courseId: string, body: PostCourseReview) =>
    await api.post(`${REVIEWS_BASE_URL}/courses/${courseId}`, body),
  update: async (reviewId: string, body: PostCourseReview) =>
    await api.put(`${REVIEWS_BASE_URL}/${reviewId}`, body),
  delete: async (reviewId: string) =>
    await api.delete(`${REVIEWS_BASE_URL}/${reviewId}`),
};
