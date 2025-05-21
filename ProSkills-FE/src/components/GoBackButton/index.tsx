import { Button, Flex } from "antd";
import { RollbackOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router";

interface GoBackButtonProps {
  justifyContent?:
    | "flex-start"
    | "flex-end"
    | "center"
    | "space-between"
    | "space-around"
    | "space-evenly";
}

const GoBackButton: React.FC<GoBackButtonProps> = ({
  justifyContent = "flex-end",
}) => {
  const navigate = useNavigate();

  return (
    <Flex justify={justifyContent}>
      <Button onClick={() => navigate(-1)} type="dashed">
        Go Back
        <RollbackOutlined />
      </Button>
    </Flex>
  );
};

export default GoBackButton;
