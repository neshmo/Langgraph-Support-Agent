const API_BASE_URL = 'http://localhost:8000';

/**
 * Submit a support ticket to the backend.
 * @param {string} text - The ticket content.
 * @returns {Promise<object>} The server response.
 */
export async function submitTicket(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/tickets/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Stream a ticket submission.
 * @param {string} text - User message
 * @param {string|null} ticketId - Optional existing ticket ID for follow-ups
 * @param {Object} callbacks - { onChunk, onTicketId, onComplete, onError }
 */
export async function streamTicket(text, ticketId, { onChunk, onTicketId, onComplete, onError }) {
    try {
        const body = { text };
        if (ticketId) {
            body.ticket_id = ticketId;  // Follow-up on existing ticket
        }

        const response = await fetch(`${API_BASE_URL}/tickets/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error(`Stream connection failed: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            // Decode chunk and add to buffer
            buffer += decoder.decode(value, { stream: true });

            // Process complete events in buffer (SSE format: data: {...}\n\n)
            const parts = buffer.split('\n\n');
            // Keep the last part if incomplete
            buffer = parts.pop();

            for (const part of parts) {
                if (part.startsWith('data: ')) {
                    const jsonStr = part.slice(6);
                    try {
                        const event = JSON.parse(jsonStr);

                        if (event.type === 'chunk') {
                            onChunk(event.content);
                        } else if (event.type === 'ticket_id') {
                            onTicketId(event.id);
                        } else if (event.type === 'final_result') {
                            onComplete(event.data);
                        } else if (event.type === 'error') {
                            onError(event.error);
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE event:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Stream Error:', error);
        onError(error.message);
    }
}

/**
 * Fetch list of tickets, optionally filtered by status.
 * @param {string} [status] - Filter by status (e.g., 'waiting_human').
 * @returns {Promise<Array>} List of tickets.
 */
export async function getTickets(status) {
    try {
        const url = new URL(`${API_BASE_URL}/tickets/`);
        if (status) {
            url.searchParams.append('status', status);
        }
        // Cache busting: Force fresh request
        url.searchParams.append('_', Date.now());

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch tickets');

        return await response.json();
    } catch (error) {
        console.error('Fetch tickets error:', error);
        throw error;
    }
}

/**
 * Submit feedback for a ticket (resolve it).
 * @param {object} payload - { ticket_id, ticket_text, final_response, feedback }
 * @returns {Promise<object>}
 */
export async function submitFeedback(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to submit feedback');
        }

        return await response.json();
    } catch (error) {
        console.error('Feedback error:', error);
        throw error;
    }
}

/**
 * Check backend health.
 */
export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return await response.json();
    } catch (error) {
        console.error('Health Check Failed:', error);
        return { status: 'offline' };
    }
}
