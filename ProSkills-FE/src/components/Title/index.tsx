import { theme, Typography } from "antd";
import { TitleProps } from "antd/es/typography/Title";

const TitleComp: React.FC<{
  children: React.ReactNode;
  props?: TitleProps;
}> = ({ children, props }) => {
  const { token: themeToken } = theme.useToken();

  return (
    <Typography.Title
      level={2}
      style={{ color: themeToken.colorPrimaryActive }}
      {...props}
    >
      {children}
    </Typography.Title>
  );
};

export default TitleComp;
