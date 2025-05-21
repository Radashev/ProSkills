import { useState, useMemo } from "react";
import { Link } from "react-router";
import {
  Table,
  Flex,
  theme,
  Tag,
  Rate,
  Button,
  Grid,
  notification,
} from "antd";
import type { TableColumnsType } from "antd";
import { GetCourse, CourseActionConfig, CoursePage } from "../../models/Course";
import { userAvailableCourseActionsByPage } from "../../constants/availableCourseActions";
import CourseActionsComp from "../CourseActions";
import { getCategoryColor } from "../../utils/courseUtils";
import { useAuthStore } from "../../store/useAuthStore";
import { GUEST_ROLE, UserRoles } from "../../models/User";
import { PATHS } from "../../routes/paths";
import SearchInput from "../SearchInput";
import TitleComp from "../Title";

const { useBreakpoint } = Grid;

const CoursesList: React.FC<{
  courses: GetCourse[];
  mode?: CoursePage;
}> = ({ courses, mode = CoursePage.AllCourses }) => {
  const role = useAuthStore((state) => state.user?.role) || GUEST_ROLE;
  const isTeacher = role === UserRoles.TEACHER;
  const availableActions = useMemo(
    () => userAvailableCourseActionsByPage[mode][role],
    [mode, role]
  );

  const screens = useBreakpoint();
  const isSmallScreen = !screens.md && (screens.xs || screens.sm);
  const actionsBlockJustify = isSmallScreen
    ? "center"
    : isTeacher && mode === "myCourses"
    ? "space-between"
    : "center";

  const [searchText, setSearchText] = useState("");
  const [deletedCourseIds, setDeletedCourseIds] = useState<number[]>([]);
  const [coursesRatings, setCoursesRatings] = useState<Record<number, number>>(
    {}
  );

  const [api, contextHolder] = notification.useNotification();

  const filteredCourses = useMemo(
    () =>
      courses
        .filter((course) => !deletedCourseIds.includes(course.id))
        .filter(
          (item) =>
            item.title.toLowerCase().includes(searchText.toLowerCase()) ||
            item.category.toLowerCase().includes(searchText.toLowerCase())
        ),
    [courses, deletedCourseIds, searchText]
  );

  const handleCourseDelete = (courseId: number) => {
    setDeletedCourseIds((prev) => [...prev, courseId]);
  };

  const columns = useMemo<TableColumnsType<GetCourse>>(
    () => [
      {
        title: "Name",
        dataIndex: "title",
        showSorterTooltip: { target: "full-header" },
        filters: filteredCourses.map((course: GetCourse) => ({
          text: course.title,
          value: course.id,
        })),
        onFilter: (value, record) => record.id === value,
        sorter: (a, b) => a.title.length - b.title.length,
      },
      {
        title: "Category",
        dataIndex: "category",
        responsive: ["sm"],
        showSorterTooltip: { target: "full-header" },
        filters: Array.from(
          new Set(filteredCourses.map((course: GetCourse) => course.category))
        ).map((category) => ({
          text: category,
          value: category,
        })),
        onFilter: (value, record) => record.category === value,
        sorter: (a, b) => a.title.length - b.title.length,
        render: (category: string) => (
          <Tag color={getCategoryColor(category)}>{category}</Tag>
        ),
      },
      {
        title: "Rating",
        dataIndex: "rating",
        responsive: ["md"],
        showSorterTooltip: { target: "full-header" },
        sorter: (a, b) => a.rating - b.rating,
        render: (rating: number, record: GetCourse) => (
          <Flex align="center" justify="center">
            <Rate
              disabled
              allowHalf
              value={coursesRatings[record.id] || rating}
            />
          </Flex>
        ),
      },
      {
        title: "",
        dataIndex: "actions",
        render: (_, record: GetCourse) => (
          <CourseActionsComp
            course={record}
            actions={availableActions}
            mode={mode}
            onDelete={() => handleCourseDelete(record.id)}
          />
        ),
      },
    ],
    [filteredCourses, coursesRatings, availableActions, mode]
  );

  return (
    <Flex vertical align="center" gap={20}>
      {contextHolder}
      <TitleComp>
        {mode === "myCourses" ? "My Courses" : "Find Your Next Course"}
      </TitleComp>
      <Flex
        justify={actionsBlockJustify}
        align="center"
        gap={15}
        wrap
        style={{ width: "100%" }}
      >
        {isTeacher && mode === "myCourses" && (
          <Link to={PATHS.NEW_COURSE.link}>
            <Button type="primary">Add New</Button>
          </Link>
        )}
        <SearchInput onChange={(e) => setSearchText(e.target.value)} />
      </Flex>
      <Table<GetCourse>
        columns={columns}
        dataSource={filteredCourses}
        showSorterTooltip={{ target: "sorter-icon" }}
        pagination={{ defaultPageSize: 6, hideOnSinglePage: true }}
        style={{ width: "100%" }}
      />
    </Flex>
  );
};

export default CoursesList;
