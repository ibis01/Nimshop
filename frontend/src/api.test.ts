import { describe, it, expect } from 'vitest';

describe('API Module', () => {
  it('should be defined and export expected functions', async () => {
    const api = await import('./api');
    expect(api).toBeDefined();
  });
});
