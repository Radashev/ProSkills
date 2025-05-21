import { userAvailableCourseActions } from "../constants/availableCourseActions";
import { UserAvailableCourseActions } from "../models/Course";

export const getCategoryColor = (category: string | undefined) => {
  if (!category) return "blue"; // Default color for undefined category

  const colors = [
    "blue",
    "green",
    "gold",
    "purple",
    "magenta",
    "cyan",
    "lime",
    "orange",
    "red",
    "geekblue",
  ];
  const index =
    category.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
    colors.length;
  return colors[index];
};

export const getUserAvailableCourseActionsByPage = (
  page: keyof (typeof userAvailableCourseActions)[keyof typeof userAvailableCourseActions][number]["visible"]
): UserAvailableCourseActions => {
  return Object.keys(userAvailableCourseActions).reduce((acc, role) => {
    acc[role] = userAvailableCourseActions[role].filter(
      (action) => action.visible[page]
    );
    return acc;
  }, {} as UserAvailableCourseActions);
};
