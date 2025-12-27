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

export const searchProducts = async (query, filters = {}) => {
    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, filters }),
        });

        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Search request failed:', error);
        throw error;
    }
};
