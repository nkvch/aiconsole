import { getBaseURL } from '../../store/useAPIStore';

export class AuthAPI {
  static async getCurrentUser() {
    const response = await fetch(`${getBaseURL()}/api/auth/me`, {
      credentials: 'include',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }

    return response.json();
  }

  static loginWithGithub() {
    window.location.href = `${getBaseURL()}/api/auth/login/github`;
  }
}
