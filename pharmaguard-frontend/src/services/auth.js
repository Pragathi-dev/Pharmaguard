// Authentication helper service for PharmaGuard Doctor Portal

const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "pharmaguard_doctor_token";
const USER_KEY = "pharmaguard_doctor_user";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const removeToken = () => localStorage.removeItem(TOKEN_KEY);

export const getCurrentUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
};

export const setCurrentUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const removeCurrentUser = () => localStorage.removeItem(USER_KEY);

export const logoutDoctor = () => {
  removeToken();
  removeCurrentUser();
};

export const registerDoctor = async ({ name, doctor_id, hospital, email, password }) => {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, doctor_id, hospital, email, password })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Registration failed. Please try again.");
  }

  setToken(data.access_token);
  setCurrentUser(data.doctor);
  return data;
};

export const loginDoctor = async (email, password) => {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Invalid email or password.");
  }

  setToken(data.access_token);
  setCurrentUser(data.doctor);
  return data;
};

export const fetchDoctorProfile = async () => {
  const token = getToken();
  if (!token) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) return null;
    const user = await res.json();
    setCurrentUser(user);
    return user;
  } catch (e) {
    return null;
  }
};

export const fetchDoctorReports = async () => {
  const token = getToken();
  try {
    const res = await fetch(`${API_BASE_URL}/api/reports`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    return [];
  }
};
