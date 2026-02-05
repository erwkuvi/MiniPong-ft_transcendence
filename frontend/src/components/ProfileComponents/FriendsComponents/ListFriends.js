import { useTranslation } from "react-i18next";

const UserList = ({ friends, onlineStatuses }) => {
  const { t } = useTranslation();

  return (
    <>
      {friends.map((user) => (
        <div key={user.id} style={{ marginBottom: "8px" }}>
          {user.username}
          {onlineStatuses[user.id] && (
            <span
              style={{
                width: "10px",
                height: "10px",
                backgroundColor: "green",
                borderRadius: "50%",
                display: "inline-block",
                marginLeft: "8px",
              }}
            ></span>
          )}
        </div>
      ))}

    </>
  );
};

export default UserList;
