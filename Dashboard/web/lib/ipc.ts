class APIClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint: string): Promise<any> {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("API request error:", error);
            return null;
        }
    }
}

const api = new APIClient("http://127.0.0.1:25400");

export async function getAllCommands(): Promise<any> {
    return api.request("/get_all_commands");
}

export async function getDetailedStats(): Promise<any> {
    return api.request("/get_detailed_stats");
}