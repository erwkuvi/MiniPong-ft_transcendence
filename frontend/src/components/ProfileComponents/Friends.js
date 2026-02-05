import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import ListFriends from "./FriendsComponents/ListFriends";
import Filter from "./FriendsComponents/Filter";
import ListUsers from "./FriendsComponents/ListUsers";

const Friends = ({
  friends,
  allUsers,
  setAllUsers,
  setFriends,
  personLoggedIn,
  onlineStatuses,
}) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [filterUsers, setFilterUsers] = useState([]);

  const handleSearch = (event) => {
    const currFiltered = event.target.value;
    setQuery(currFiltered);
    if (!currFiltered) {
      setFilterUsers([]);
    } else {
      const filteredUsers = allUsers.filter((user) =>
        user.username.toLowerCase().includes(currFiltered.toLowerCase()),
      );
      setFilterUsers(filteredUsers);
    }
  };

  return (
    <div className="profileCardStyle1" style={{ textAlign: "center" }}>
      <h2>{t("List of friends")}</h2>
      <ListFriends friends={friends} onlineStatuses={onlineStatuses} />
      <Filter
        className="inputFieldStyle1"
        placeholder={t("Search for users")}
        type="text"
        value={query}
        onChange={handleSearch}
        aria-label={t("Search for users")}
      />
      <ListUsers
        filterUsers={filterUsers}
        setAllUsers={setAllUsers}
        setFilterUsers={setFilterUsers}
        setFriends={setFriends}
        personLoggedIn={personLoggedIn}
      />
    </div>
  );
};

export default Friends;
