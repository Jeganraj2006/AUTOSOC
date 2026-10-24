import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchApi, ApiError } from './api';

describe('fetchApi', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  it('should return JSON data on success', async () => {
    const mockData = { test: 'value' };
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    } as Response);

    const result = await fetchApi('/test');
    expect(result).toEqual(mockData);
  });

  it('should throw ApiError on non-2xx response', async () => {
    const mockErrorData = { error_code: 'ERR', message: 'Something went wrong' };
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => mockErrorData,
    } as Response);

    await expect(fetchApi('/test')).rejects.toThrow(ApiError);
  });
});
