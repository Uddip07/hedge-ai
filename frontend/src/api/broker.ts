/**
 * Broker REST API Client for Frontend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface BrokerProfile {
  user_id: string;
  user_name: string;
  email: string;
  user_type: string;
  broker: string;
  exchanges: string[];
  products: string[];
  order_types: string[];
  avatar_url?: string;
}

export interface BrokerFunds {
  net: number;
  available_cash: number;
  available_collateral: number;
  utilised_debits: number;
  segment: string;
}

export const fetchBrokerProfile = async (baseUrl: string = API_BASE_URL): Promise<BrokerProfile | null> => {
  try {
    const response = await axios.get(`${baseUrl}/broker/profile`);
    return response.data;
  } catch {
    return null;
  }
};

export const fetchBrokerFunds = async (baseUrl: string = API_BASE_URL): Promise<BrokerFunds | null> => {
  try {
    const response = await axios.get(`${baseUrl}/broker/funds`);
    return response.data;
  } catch {
    return null;
  }
};

export const fetchBrokerHoldings = async (baseUrl: string = API_BASE_URL) => {
  const response = await axios.get(`${baseUrl}/broker/holdings`);
  return response.data;
};

export const fetchBrokerPositions = async (baseUrl: string = API_BASE_URL) => {
  const response = await axios.get(`${baseUrl}/broker/positions`);
  return response.data;
};

export const fetchBrokerOrders = async (baseUrl: string = API_BASE_URL) => {
  const response = await axios.get(`${baseUrl}/broker/orders`);
  return response.data;
};
