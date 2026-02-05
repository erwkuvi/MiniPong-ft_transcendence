import React, { useEffect, useState, useContext, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AccessibilityContext } from "../AccessibilityContext";
import { AuthContext } from "../context/AuthContext";
import { ProfileContext } from "../context/ProfileContext";
import useWindowDimensions from "../components/userWindowDimensions";
import { fetchUsers } from "../services/fetchUsers";
import { getUserProfile } from "../services/getProfile";
import Friends from "../components/ProfileComponents/Friends";
import ProfileBasicInfo from "../components/ProfileComponents/ProfileBasicInfo";
import PasswordModal from "../components/PasswordModal";
import StatisticsCard from "../components/ProfileComponents/StatisticsCard";
import Otp from "../components/OTPActivationModal";
import "./Profile.css";

const Profile = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { height } = useWindowDimensions();
  const [status, setStatus] = useState("");
  const { fontSize } = useContext(AccessibilityContext);
  const scaleStyle = { fontSize: `${fontSize}px` };
  const { isLoggedIn } = useContext(AuthContext);

  const {
    setIsSaving2FA,
    loading,
    setLoading,
    profile,
    setProfile,
    personLoggedIn,
    setPersonLoggedIn,
    isPasswordModalOpen,
    setPasswordModalOpen,
    isOtpActive,
    setOtpActive,
    setNewDisplayName,
  } = useContext(ProfileContext);

  const [friends, setFriends] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [error, setError] = useState(null);
  const [onlineStatuses, setOnlineStatuses] = useState({});

  const wsBaseUrl = process.env.REACT_APP_BACKEND_WS;
  const user_id = localStorage.getItem("user_id");

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
    }
  }, [navigate, isLoggedIn]);

  const loadProfile = async () => {
    try {
      const profileData = await getUserProfile();
      localStorage.setItem("user_id", profileData.user_id);
      localStorage.setItem("display_name", profileData.display_name);

      setProfile(profileData);
      setNewDisplayName(profileData.display_name);

      const users = await fetchUsers();
      const loggedInUser = users.find(
        (user) => user.username === profileData.username,
      );
      setPersonLoggedIn(loggedInUser);

      const otherUsers = users.filter(
        (user) => user.username !== profileData.username,
      );
      setAllUsers(otherUsers);

      const friendsList = otherUsers.filter((user) =>
        profileData.friends.includes(user.id),
      );
      setFriends(friendsList);
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!user_id) return;

    const wsUrl = `${wsBaseUrl}/ws/online-status/?user_id=${user_id}&token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
    //   console.log("✅ WebSocket connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
    //   console.log("📩 Received status:", data);

      setOnlineStatuses((prev) => ({
        ...prev,
        [String(data.user_id)]: data.is_online,
      }));
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket disconnected");
    };

    return () => ws.close();
  }, [user_id]);

  const handlePasswordSuccess = () => {
    setIsSaving2FA(true);
    setPasswordModalOpen(false);
    setOtpActive(true);
  };

  if (loading || !isLoggedIn) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!profile) return <p>No profile data available</p>;

  return (
    <div
      className="d-flex flex-column align-items-center w-100 profilePageHolder"
      id="profilePageHolder"
      style={{ minHeight: `${height - 90}px` }}
    >
      <h1 className="pageHeadingH1Style1 profileHeading">
        {t("HeaderProfile")}
      </h1>
      <div className="profileCardHolder  mb-0 w-100" style={scaleStyle}>
        <ProfileBasicInfo loadProfile={loadProfile} style={scaleStyle} />
        <StatisticsCard
          losses={profile.losses}
          wins={profile.wins}
          fontSize={fontSize}
        />
        <Friends
          friends={friends}
          allUsers={allUsers}
          setAllUsers={setAllUsers}
          setFriends={setFriends}
          personLoggedIn={personLoggedIn}
          onlineStatuses={onlineStatuses}
        />
      </div>
      <PasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setPasswordModalOpen(false)}
        onSubmit={handlePasswordSuccess}
        onPasswordSuccess={handlePasswordSuccess}
      />
      {isOtpActive && (
        <Otp
          onSuccess={() => {
            setOtpActive(false);
            setIsSaving2FA(false);
            setProfile((prev) => ({
              ...prev,
              otp_active: !prev.otp_active,
            }));
          }}
        />
      )}
    </div>
  );
};

export default Profile;
