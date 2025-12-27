const API_URL = 'http://localhost:8000';

export const checkBackendHealth = async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            throw new Error('Backend unreachable');
        }
        return await response.json();
    } catch (error) {
        console.error('Backend health check failed:', error);
        throw error;
    }
};
