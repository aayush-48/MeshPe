const BASE_URL = 'http://localhost:8000';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

async function fetchWithCredentials(url: string, options: RequestInit = {}): Promise<Response> {
  console.log(`[ApiClient] Fetching ${url}...`);
  try {
    const response = await fetch(`${BASE_URL}${url}`, {
      ...options,
      credentials: 'include',
      headers: {
        ...options.headers,
      },
    });
    console.log(`[ApiClient] Response status: ${response.status}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`[ApiClient] Error data:`, errorData);
      throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (e) {
    console.error(`[ApiClient] Fetch failed:`, e);
    throw e;
  }
}

export async function signup(formData: FormData): Promise<ApiResponse> {
  try {
    const response = await fetchWithCredentials('/auth/signup', {
      method: 'POST',
      body: formData,
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Signup failed',
    };
  }
}

export async function loginStart(userId: string): Promise<ApiResponse<{ challenge: string }>> {
  try {
    const response = await fetchWithCredentials('/auth/login/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Login start failed',
    };
  }
}

export async function loginVerify(formData: FormData): Promise<ApiResponse<{ user: any }>> {
  try {
    const response = await fetchWithCredentials('/auth/login/verify', {
      method: 'POST',
      body: formData,
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Login verification failed',
    };
  }
}

export async function initiatePayment(formData: FormData): Promise<ApiResponse<{
  payment_info: {
    receiver_name: string;
    amount: number;
    currency: string;
  };
  raw_text?: string;
}>> {
  try {
    const response = await fetchWithCredentials('/payment/initiate', {
      method: 'POST',
      body: formData,
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Payment initiation failed',
    };
  }
}

export async function confirmPayment(formData: FormData): Promise<ApiResponse<{
  payment_info: {
    receiver_name: string;
    amount: number;
    currency: string;
  };
}>> {
  try {
    const response = await fetchWithCredentials('/payment/confirm', {
      method: 'POST',
      body: formData,
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Payment confirmation failed',
    };
  }
}

export async function addContact(userId: string, contactName: string, contactId: string): Promise<ApiResponse> {
  try {
    const response = await fetchWithCredentials(`/auth/contacts/add?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contact_name: contactName, contact_id: contactId }),
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Add contact failed',
    };
  }
}

export async function getContacts(userId: string): Promise<ApiResponse<{ contacts: Array<{ name: string; id: string }> }>> {
  try {
    const response = await fetchWithCredentials(`/auth/contacts/list?user_id=${encodeURIComponent(userId)}`, {
      method: 'GET',
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Fetch contacts failed',
    };
  }
}

export async function logout(): Promise<ApiResponse> {
  try {
    const response = await fetchWithCredentials('/auth/logout', {
      method: 'POST',
    });
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Logout failed',
    };
  }
}
