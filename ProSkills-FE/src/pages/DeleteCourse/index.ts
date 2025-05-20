import { useEffect } from "react";
import { Modal } from "antd";
import { useNavigate, useParams, useSubmit } from "react-router";
import { coursesApi } from "../../api/courses";

const DeleteCoursePage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const submit = useSubmit();

  useEffect(() => {
    Modal.confirm({
      title: "Delete Course",
      content: "Are you sure you want to delete this course?",
      okText: "Yes",
      cancelText: "No",
      onOk: () => {
        submit(null, { method: "post", action: `/courses/${courseId}/delete` });
      },
      onCancel: () => {
        navigate(-1);
      },
    });
  }, [courseId, navigate, submit]);

  return null;
};

export default DeleteCoursePage;

export async function action({ params }: { params: { courseId: string } }) {
  try {
    const response = await coursesApi.delete(params.courseId);

    return { error: "Failed to delete course" };
  } catch (error) {
    return { error: "Something went wrong" };
  }
}
