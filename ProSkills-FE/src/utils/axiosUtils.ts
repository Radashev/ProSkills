import axios, { AxiosError, AxiosResponse } from "axios";
import { ArgsProps } from "antd/es/notification";
import { NotificationInstance } from "antd/es/notification/interface";
import { APIError } from "../models/APIResponse";
import { useAuthStore } from "../store/useAuthStore";
import { resolve } from "path";

const defaultNotificationConfig: ArgsProps = {
  message: "Attempt Unsuccessful",
  description: "An unexpected error occurred.",
  placement: "topRight",
  duration: 10,
};

export function getAxiosError(error: unknown) {
  if (axios.isAxiosError(error)) {
    return error;
  }

  throw new Error("Unexpected error occurred while making a request.");
}

export const handleAxiosRequest = async <T>(
  requestFunction: () => Promise<AxiosResponse<T>>,
  notification: NotificationInstance,
  userMessageSuccess: string,
  customConfig?: Partial<ArgsProps>
): Promise<boolean> => {
  const notificationConfig: ArgsProps = {
    ...defaultNotificationConfig,
    ...customConfig,
  };

  try {
    const response: AxiosResponse<T> = await requestFunction();

    if (response?.status && response.status >= 200 && response.status < 300) {
      notification.success({
        ...notificationConfig,
        message: "Attempt Successful",
        description: userMessageSuccess,
      });
      return true;
    }
    return false;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        const { checkAuth } = useAuthStore.getState();
        await checkAuth();

        const { user } = useAuthStore.getState();
        if (user?.id) {
          return await handleAxiosRequest(
            requestFunction,
            notification,
            userMessageSuccess,
            customConfig
          );
        } else {
          handleAxiosError(error, notification, notificationConfig);
          return false;
        }
      } else {
        handleAxiosError(error, notification, notificationConfig);
        return false;
      }
    } else {
      console.error("Unexpected error:", error);
      return false;
    }
  }
};


export const handleAxiosError = (
  error: AxiosError<APIError>,
  notification?: NotificationInstance,
  customConfig?: Partial<ArgsProps>
) => {
  const notificationConfig: ArgsProps = {
    ...defaultNotificationConfig,
    ...customConfig,
  };

  const errorDetail = error.response?.data?.detail;

  if (errorDetail) {
    let errorDescription = "An error occurred.";

    if (Array.isArray(errorDetail)) {
      errorDescription = errorDetail[0]?.msg || errorDescription;
    } else if (typeof errorDetail === "string") {
      errorDescription = errorDetail;
    }

    notificationConfig.description = errorDescription;
  }

  if (notification) {
    notification.error(notificationConfig);
  }
};
