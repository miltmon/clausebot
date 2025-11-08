const nock = require('nock');
process.env.LLM_API_URL = 'https://api.openai.com/v1/chat/completions';
process.env.LLM_API_KEY = 'test';
process.env.LLM_SANITIZE = 'true';
process.env.LLM_CONTEXT_MAX_CHARS = '100';

const { callLLM } = require('../llmClient');

describe('llmClient', () => {
  afterEach(() => nock.cleanAll());

  it('rejects payloads above LLM_CONTEXT_MAX_CHARS', async () => {
    const big = 'x'.repeat(120);
    const pageObj = { title: big, snippet: big };
    const selectors = [{ name: 'title' }, { name: 'snippet' }];
    await expect(
      callLLM({ task: 't', schema: { type: 'object' }, pageObj, selectors, runId: 'r' })
    ).rejects.toThrow('context_limit_exceeded');
  });

  it('returns schema-shaped JSON (mocked)', async () => {
    process.env.LLM_CONTEXT_MAX_CHARS = '1000';
    nock('https://api.openai.com').post('/v1/chat/completions').reply(200, {
      choices: [{ message: { content: '{"ok":true,"items":[]}' } }]
    });
    const pageObj = { title: 'short', snippet: 'short' };
    const selectors = [{ name: 'title' }, { name: 'snippet' }];
    const res = await callLLM({ task: 'extract', schema: { type: 'object' }, pageObj, selectors, runId: 'r' });
    expect(res).toBeTruthy();
  });
});
