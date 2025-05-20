import { Col, notification as antdNotification, Row, Flex } from "antd";
import { useState } from "react";
import { GetCourse, CourseActionConfig } from "../../models/Course";
import CourseActionRenderer from "../CourseActionRenderer";

const CourseActionsComp: React.FC<{
  course: GetCourse;
  actions: CourseActionConfig[];
  mode?: string | null;
  onDelete?: () => void;
}> = ({ course, actions = [], mode = "", onDelete }) => {
  const [notification, contextHolder] = antdNotification.useNotification();
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDelete = () => {
    setShowDeleteModal(false);
    onDelete?.();
  };

  return (
    <>
      <Row
        gutter={[8, 8]}
        justify="center"
        style={{ display: "flex", flexWrap: "wrap" }}
      >
        {actions.map((action: CourseActionConfig) => (
          <Col
            key={`${action.title}-${course.id}`}
            style={{ flex: "1 1 auto", maxWidth: "200px" }}
          >
            {
              <CourseActionRenderer
                action={action}
                course={course}
                notification={notification}
                showDeleteModal={showDeleteModal}
                setShowDeleteModal={setShowDeleteModal}
                mode={mode}
                onDelete={handleDelete}
              />
            }
          </Col>
        ))}
      </Row>
      {contextHolder}
    </>
  );
};

export default CourseActionsComp;
