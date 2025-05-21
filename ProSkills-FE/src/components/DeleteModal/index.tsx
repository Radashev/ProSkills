import { useEffect } from "react";
import { Modal, notification } from "antd";
import { AxiosResponse } from "axios";
import { CourseAssignment, GetCourse } from "../../models/Course";
import { Student } from "../../models/Student";

const { confirm } = Modal;

interface DeleteModalProps {
  data: GetCourse | Student | CourseAssignment;
  deleteRequest: () => Promise<AxiosResponse<any>>;
  onClose: () => void;
  onSuccess?: () => void;
}

const DeleteModal: React.FC<DeleteModalProps> = ({
  data,
  deleteRequest,
  onClose,
  onSuccess,
}) => {
  useEffect(() => {
    const modal = confirm({
      title: "Are you sure you want to delete it?",
      content: "This action cannot be undone.",
      okText: "Yes",
      okType: "danger",
      cancelText: "No",
      onOk: async () => {
        try {
          const response = await deleteRequest();
          if (response.status === 200) {
            notification.success({
              message: "Deleted successfully",
            });
            if (onSuccess) {
              onSuccess();
            }
          } else {
            notification.error({
              message: "Failed to delete",
            });
          }
        } catch (error) {
          notification.error({
            message: "An error occurred while deleting",
          });
        } finally {
          onClose();
        }
      },
      onCancel: () => {
        onClose();
      },
    });

    return () => {
      modal.destroy();
    };
  }, [data, onClose, deleteRequest, onSuccess]);

  return null;
};

export default DeleteModal;
