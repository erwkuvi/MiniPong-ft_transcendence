import React, { useState, useRef, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { updateUserProfile } from '../../services/patchUserProfile';
import axiosInstance from '../../services/axiosInstance';
import { ProfileContext } from '../../context/ProfileContext';

const ProfileBasicInfo = ({ loadProfile, style }) => {
	const { t } = useTranslation();
	const [error, setError] = useState('');
	const fileInputRef = useRef(null);
	const {	profile, setProfile, 
				setPasswordModalOpen, 
				isSaving2FA, setIsSaving2FA } = useContext(ProfileContext);
		
	const [isEditingDisplayName, setIsEditingDisplayName] = useState(false);
	const [newDisplayName, setNewDisplayName] = useState(profile.display_name);
	const BASE_URL = process.env.REACT_APP_BACKEND_URL;

 	const handleEditDisplayName = () => setIsEditingDisplayName(true);

  const handleSaveDisplayName = async () => {
    if (!newDisplayName || newDisplayName === profile.display_name) return;
	if (newDisplayName.length < 3) {
		setError(t('Display name must be at least 3 characters long.'));
		return;
	}

	if (newDisplayName.length > 15) {
		setError(t('Display name must be not more than 15 characters long.'));
		return;
	}

    try {
      const updatedProfile = await updateUserProfile({ display_name: newDisplayName });
      setProfile(updatedProfile);
	  localStorage.setItem('display_name', newDisplayName);
      setIsEditingDisplayName(false);
      await loadProfile();
    } catch (err) {
      console.error('Error updating display name:', err);
      setError(t('Failed to update display name'));
    }
  };

  const handleCancelEdit = () => {
    setNewDisplayName(profile.display_name);
    setIsEditingDisplayName(false);
  };

  const handleEditAvatar = () => fileInputRef.current.click();

  const handleAvatarChange = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
	  setError('Please select an image file');
      return;
    }

    try {
      const updatedProfile = await updateUserProfile({ avatar: file });
      setProfile(updatedProfile);
      await loadProfile();
    } catch (err) {
      console.error('Error updating avatar:', err);
      setError(t('Failed to update avatar'));
    }
  };

  const handleInitiateToggle2FA = () => {
	if (!profile.otp_active) {
		setPasswordModalOpen(true);
	} else {
		handleToggle2FA();
	}
};

  const handleToggle2FA = async (password = null) => {
	
	setIsSaving2FA(true);
	const userId = localStorage.getItem('user_id');
	const token = localStorage.getItem('access_token');

	try {
		const response = await axiosInstance.post(
			`${BASE_URL}/user_management/otp-active-to-false/`,
			{
				user_id: userId
			},
			{
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `JWT ${token}`
				}
			}
		);

		setProfile(prev => ({
			...prev,
			otp_active: !prev.otp_active
		}));
			
	} catch (err) {
		console.error('Error updating 2FA status:', err);
	} finally {
		setIsSaving2FA(false);
	}
};

  return (
    <div className='profileCardStyle1' style={style} >
      <h2>{t("Basic Information")}</h2>
      <div className="d-flex flex-row flex-wrap align-items-center justify-content-center">
        <img 	
			src={profile.avatar} 
			className='profilepic m-2' 
			alt={`${profile.display_name}'s avatar`} 
			tabIndex="0" 
		/>
        <input 
			type="file" 
			ref={fileInputRef} 
			onChange={handleAvatarChange} 
			accept="image/*" 
			className="sr-only" 
			style={{ display: 'none' }} 
			aria-label={t("Upload avatar image")} 
		/>
        <button 
			onClick={handleEditAvatar} 
			className="edit-avatar-button" 
			title="Edit avatar" 
			aria-label={t("Edit avatar")}
		>
        	<span className="edit-pic">📷</span>
        </button>
      </div>
      <div id="profileBasicInfoInformationHolder">
        <p>{t("Username")} <span>{profile.username}</span></p>
        <p id="profileDisplayChangeName">
          {t("Display Name")}
          {isEditingDisplayName ? (
            <>
            	<input 
					type="text" 
					value={newDisplayName} 
					onChange={(e) => setNewDisplayName(e.target.value)} 
					className="change-display-name-input" 
					aria-label={t("Edit display name")} 
				/>
              	<span id="profileEditDisplayNameButtonHolder">
                <button 
					onClick={handleSaveDisplayName} 
					className="profileButtonChangeNameSaveCancel" 
					title="Save"
				>
                	<span className="text-green-600">✓</span>
                </button>
                <button 
					onClick={handleCancelEdit} 
					className="profileButtonChangeNameSaveCancel" 
					aria-label={t("Cancel display name edit")} 
					title="Cancel"
				>
                	<span className="text-red-600">✕</span>
                </button>
              </span>
            </>
          ) : (
            <span id="profilePenAndNameHolder">
              <span>{profile.display_name + ' '}</span>
              <button 
				onClick={handleEditDisplayName} 
				id="profileEditDisplayNameButton" 
				title="Edit display name" 
				aria-label={t("Edit display name")}
				>
        		<span className="write-symbol">✎</span>
              </button>
            </span>
          )}
        </p>
		{error && <p className="tfa-message">{error}</p>}
        <p>{t("email")} <span>{profile.email}</span></p>
      </div>
	  {profile.auth_provider !== "42api" && profile.auth_provider !== "google" && (
		<div className="mt-4">
			<button
				onClick={handleInitiateToggle2FA}
				disabled={isSaving2FA}
				className="buttonStyle1"
				aria-label={profile.otp_active ? t("Disable 2FA") : t("Enable 2FA")}
			>
				{isSaving2FA ? t("Saving...") : profile.otp_active ? t("Disable 2FA") : t("Enable 2FA")}
			</button>
		</div>
		)}
	</div>
  );
};

export default ProfileBasicInfo;
