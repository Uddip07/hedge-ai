/**
 * Broker REST API Client for Frontend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const fetchBrokerProfile = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/profile`);
    return response.data;
  } catch {
    return null;
  }
};

export const fetchBrokerFunds = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/funds`);
    return response.data;
  } catch {
    return null;
  }
};

export const fetchBrokerHoldings = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/holdings`);
    return response.data;
  } catch {
    return [];
  }
};

export const fetchBrokerPositions = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/positions`);
    return response.data;
  } catch {
    return { net: [], day: [] };
  }
};

export const fetchBrokerOrders = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/orders`);
    return response.data;
  } catch {
    return [];
  }
};

export const fetchBrokerHealth = async (baseUrl = API_BASE_URL) => {
  try {
    const response = await axios.get(`${baseUrl}/broker/health`);
    return response.data;
  } catch {
    return { status: 'DEGRADED', is_authenticated: false };
  }
};

export const placeBrokerOrder = async (orderPayload, baseUrl = API_BASE_URL) => {
  const response = await axios.post(`${baseUrl}/broker/order`, orderPayload);
  return response.data;
};

export const placeBrokerGTT = async (gttPayload, baseUrl = API_BASE_URL) => {
  const response = await axios.post(`${baseUrl}/broker/gtt`, gttPayload);
  return response.data;
};
